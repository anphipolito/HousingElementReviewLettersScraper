import pandas as pd
import os
import fitz  #
import re
import datetime
import json
from pdfDownloader import download_pdf
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
            if page.get_text() == "Sincerely,": #Stop at "Sincerely" line
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
        if re.search(r"\b{}\b".format(phrase), self.pdf_text):
            return True
        else:
            return False



def main():
    pdf_dir = './pdfs/'
    df = pd.read_excel('he-review-letters.xlsx', )
    df['REVIEWED'] = pd.to_datetime(df['REVIEWED']).dt.date
    df1 = df[(df.TYPE == 'INITIAL DRAFT') & (df.REVIEWED > datetime.date(year=2020, month=1, day=1))]
    df2 = df[(df.TYPE == 'ADOPTED')][['JURISDICTION','REVIEWED']]
    df2 = df2.groupby('JURISDICTION').agg({'REVIEWED':'max'}).reset_index()

    email_dict= {'JURISDICTION':[],'EMAIL':[],'ID_DATE':[],'AD_DATE':[],'COUNTY':[],'pageCount':[],"checkP1":[],'checkP2':[],'checkP3':[]}
    for juris,url,date,county in zip(df1['JURISDICTION'],df1['LINK TO REVIEW LETTER'],df1['REVIEWED'],df1['COUNTY']):
        pdf_path = pdf_dir+ url.split("/")[-1]

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
            email_dict['checkP1'].append(checkP1)
            email_dict['checkP2'].append(checkP2)
            email_dict['checkP3'].append(checkP3)

            if adopted_date.empty:
                email_dict['AD_DATE'].append(date)
            else:
                email_dict['AD_DATE'].append(adopted_date.values[0])
            break
    for key in email_dict.keys():
        print(key,len(email_dict[key]))
    email_dict =pd.DataFrame.from_dict(email_dict)
    email_dict.to_csv('data.csv')


    # print(loaded_data)

if __name__ == "__main__":
    main()