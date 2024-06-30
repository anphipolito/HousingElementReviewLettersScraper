import pandas as pd
import os
import fitz  #
import re
import datetime
import json
from pdfDownloader import download_pdf
import pymupdf
def extract_text_from_pdf(pdf_path):
    # Open the PDF file
    document = fitz.open(pdf_path)
    text = ""
    # Iterate through each page
    for page_num in range(len(document)):
        page = document.load_page(page_num)
        text += page.get_text()
        if page.get_text() == "Sincerely,": #Stop at "Sincerely" line
            break
    return text
def extract_emails_from_text(text):
    # Define a regular expression pattern for extracting emails
    email_pattern = r'[a-zA-Z0-9._%+-]+@hcd.ca.gov'
    emails = re.findall(email_pattern, text)
    return emails

def extract_emails_from_pdf(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    emails = extract_emails_from_text(text)
    return emails

def main():
    pdf_dir = './pdfs/'
    df = pd.read_excel('he-review-letters.xlsx', )
    df['REVIEWED'] = pd.to_datetime(df['REVIEWED']).dt.date
    df1 = df[(df.TYPE == 'INITIAL DRAFT') & (df.REVIEWED > datetime.date(year=2020, month=1, day=1))]
    df2 = df[(df.TYPE == 'ADOPTED')][['JURISDICTION','REVIEWED']]
    df2 = df2.groupby('JURISDICTION').agg({'REVIEWED':'max'}).reset_index()

    email_dict= {'JURISDICTION':[],'EMAIL':[],'ID_DATE':[],'AD_DATE':[]}
    for juris,url,date in zip(df1['JURISDICTION'],df1['LINK TO REVIEW LETTER'],df1['REVIEWED']):
        pdf_path = pdf_dir+ url.split("/")[-1]
        try:
            emails = extract_emails_from_pdf(pdf_path)
        except pymupdf.FileNotFoundError: #PDF not exist
            # try: # Downloading again the pdf file
            #     print(f"{pdf_path} doesn't exist")
            #     print(f"Downloading: {pdf_path}")
            #     download_pdf(url)
            #     emails = extract_emails_from_pdf(pdf_path)
            # except: #Invalid pdf URL
            #     print("Status: Invalid url")
            continue
        emails = [email for email in emails if email != 'sitesinventory@hcd.ca.gov']
        adopted_date = df2[df2.JURISDICTION == juris].REVIEWED
        for email in emails:
            email_dict['EMAIL'].append(email)
            email_dict['JURISDICTION'].append(juris)
            email_dict['ID_DATE'].append(date)
            if adopted_date.empty:
                email_dict['AD_DATE'].append(date)
            else:
                email_dict['AD_DATE'].append(adopted_date.values[0])
    email_dict =pd.DataFrame.from_dict(email_dict)
    email_dict.to_csv('data.csv')


    # print(loaded_data)

if __name__ == "__main__":
    main()