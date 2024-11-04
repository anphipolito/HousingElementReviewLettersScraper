import pandas as pd
import fitz  #
import re
import datetime
import pymupdf
class Extract:
    def __init__(self,pdf_path):
        self.pdf_text = self.extract_text_from_pdf(pdf_path)
        self.getPageCount()
    def extract_text_from_pdf(self,pdf_path):
        # Open the PDF file
        self.document= fitz.open(pdf_path)

        text = ""
        # Iterate through each page
        for page_num in range(len(self.document)):
            page = self.document.load_page(page_num)
            text += page.get_text()
            if "Sincerely" in  page.get_text(): #Stop at "Sincerely" line
                break
            elif 'Enclosure' in page.get_text(): #Stops before Appendix page
                break
        return text
    def extract_emails_from_text(self):
        # Define a regular expression pattern for extracting emails
        email_pattern = r'[a-zA-Z0-9._%+-]+@hcd.ca.gov'
        emails = re.findall(email_pattern, self.pdf_text)
        return emails
    def extract_emails_from_pdf(self):
        emails = self.extract_emails_from_text()
        return emails

    def getPageCount(self):
        self.pageCount = len(self.document)
    def findPhrases(self,phrase):
        regex = r"\b{}\b".format(re.sub(r"\s+", r"\\s+", phrase))
        result = re.search(regex, self.pdf_text)
        if result:
            return True
        else:
            return False



def main():
    pdf_dir = './pdfs/'
    df = pd.read_excel('he-review-letters.xlsx',)
    df['REVIEWED'] = pd.to_datetime(df['REVIEWED']).dt.date
    df1 = df[(df.TYPE == 'INITIAL DRAFT') & (df.REVIEWED >= datetime.date(year=2019, month=1, day=1))]

    # the first draft is not labelled an initial draft
    unlabelled_initial_drafts = df[~df.JURISDICTION.isin(df1.JURISDICTION)]
    unlabelled_initial_drafts = unlabelled_initial_drafts[unlabelled_initial_drafts['TYPE'] == 'DRAFT']
    unlabelled_initial_drafts = unlabelled_initial_drafts[unlabelled_initial_drafts['PLANNING CYCLE'] == 6]

    # Group by JURISDICTION and return the row with the minimum 'REVIEWED' date
    unlabelled_initial_drafts = unlabelled_initial_drafts.groupby('JURISDICTION', group_keys=False).apply(
        lambda g: g.loc[g['REVIEWED'].idxmin()]
    )
    df1 = pd.concat((df1, unlabelled_initial_drafts))

    df2 = df[(df.TYPE == 'ADOPTED')][['JURISDICTION','REVIEWED']]
    df2 = df2.groupby('JURISDICTION').agg({'REVIEWED':'max'}).reset_index()

    email_dict= {'JURISDICTION':[],
                 'EMAIL':[],'ID_DATE':[],'AD_DATE':[],'COUNTY':[],
                 'pageCount':[],"checkP1":[],'checkP2':[],'checkP3':[], 'checkP4':[]}
    for juris,url,date,county in zip(df1['JURISDICTION'],df1['LINK TO REVIEW LETTER'],df1['REVIEWED'],df1['COUNTY']):
        pdf_path = pdf_dir+ url.split("/")[-1]
        print(juris,pdf_path)

        try:
            ex=Extract(pdf_path)
        except pymupdf.FileNotFoundError: #PDF not exist
            continue
        emails = ex.extract_emails_from_pdf()

        emails = [email for email in emails if email != 'sitesinventory@hcd.ca.gov']
        adopted_date = df2[df2.JURISDICTION == juris].REVIEWED
        for email in emails:


            email_dict['EMAIL'].append(email)
            email_dict['JURISDICTION'].append(juris)

            email_dict['ID_DATE'].append(date)
            email_dict['COUNTY'].append(county)
            email_dict['pageCount'].append(ex.pageCount)

            checkP1 = ex.findPhrases('addresses many statutory requirements')
            checkP2= ex.findPhrases( 'addresses some statutory requirements')
            checkP3 = ex.findPhrases( 'addresses most statutory requirements')
            checkP4 = ex.findPhrases( 'element in substantial compliance')
            checkP4 |= ex.findPhrases( 'The housing element will comply with State Housing Element Law')
            checkP4 |= ex.findPhrases( 'The housing element will comply with housing element law')
            checkP4 |= ex.findPhrases( 'The housing element will comply with State Housing Element law')
            checkP4 |= ex.findPhrases(
                'The housing element will comply when it is adopted')
            checkP4 |= ex.findPhrases('housing element will comply with the law when it is adopted')

            email_dict['checkP1'].append(checkP1)
            email_dict['checkP2'].append(checkP2)
            email_dict['checkP3'].append(checkP3)
            email_dict['checkP4'].append(checkP4)

            if adopted_date.empty:
                email_dict['AD_DATE'].append(date)
            else:
                email_dict['AD_DATE'].append(adopted_date.values[0])
            break
    for key in email_dict.keys():
        print(key,len(email_dict[key]))
    email_dict =pd.DataFrame.from_dict(email_dict)
    email_dict.to_csv('data.csv')



if __name__ == "__main__":
    main()