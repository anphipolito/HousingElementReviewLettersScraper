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
    df_orig = pd.read_excel('./he-review-letters.xlsx', )
    df_orig['REVIEWED'] = pd.to_datetime(df_orig['REVIEWED']).dt.date
    df = df_orig[(df_orig.TYPE == 'INITIAL DRAFT') & (df_orig.REVIEWED > datetime.date(year=2019, month=1, day=1))].copy()

    unlabelled_initial_drafts = df_orig[~df_orig.JURISDICTION.isin(df.JURISDICTION)]
    unlabelled_initial_drafts = unlabelled_initial_drafts[unlabelled_initial_drafts['TYPE'] == 'DRAFT']
    unlabelled_initial_drafts = unlabelled_initial_drafts[unlabelled_initial_drafts['PLANNING CYCLE'] == 6]

    # Group by JURISDICTION and return the row with the minimum 'REVIEWED' date
    unlabelled_initial_drafts = unlabelled_initial_drafts.groupby('JURISDICTION', group_keys=False).apply(
        lambda g: g.loc[g['REVIEWED'].idxmin()]
    )
    df = pd.concat((df, unlabelled_initial_drafts))

    urls = []
    for link in df['LINK TO REVIEW LETTER'].tolist():
        if '/' not in link:
            continue
        path = './pdfs/' + link.split('/')[-1]
        if os.path.exists(path):
            continue
        else:
            urls.append(link)

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(download_pdf, url) for url in urls]
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
