import pandas as pd
import datetime
import os
import concurrent.futures
from selenium import webdriver
from time import sleep
def download_pdf(lnk):

    options = webdriver.ChromeOptions()

    download_folder = os.path.abspath("./pdfs/")
    profile = {"plugins.plugins_list": [{"enabled": False,
                                         "name": "Chrome PDF Viewer"}],
               "download.default_directory": download_folder,
               "download.extensions_to_open": "",
               "plugins.always_open_pdf_externally": True}

    options.add_experimental_option("prefs", profile)

    print("Downloading file from link: {}".format(lnk))

    driver = webdriver.Chrome(options=options)
    driver.get(lnk)
    filename = lnk.split("/")[-1]
    print("File: {}".format(filename))
    sleep(5)

    driver.close()
def main():
    df = pd.read_excel('../he-review-letters.xlsx', )
    df['REVIEWED'] = pd.to_datetime(df['REVIEWED']).dt.date
    df = df[(df.TYPE == 'INITIAL DRAFT') & (df.REVIEWED > datetime.date(year=2020, month=1, day=1))]
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(download_pdf, url) for url in df['LINK TO REVIEW LETTER'].tolist()]
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
