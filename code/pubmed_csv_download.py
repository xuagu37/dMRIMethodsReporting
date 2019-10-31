import logging
import requests
import csv
import os

TOOLNAME = 'pubmed_pdf'
EMAIL = 'your_email@example.com'  # Please set if you use this extensively

API_URL = "https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?tool={toolname}&email={email}&ids={pmid}&versions=no&format=json"
PMC_PDF_URL = "https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/pdf/"
PMC_ePUB_URL = "https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/epub/"

logging.basicConfig()
logger = logging.getLogger('pubmed_pdf')

def find_url(url):
    r = requests.head(url, headers={'User-Agent': 'fetch_pmc_pdf/0.1'})
    if r.status_code == 200:
        return url
    elif r.status_code == 303:  # redirect
        return find_url(r.headers['Location'])
    else:
        return None

def find_url2(url):
    r = requests.head(url, headers={'User-Agent': 'fetch_pmc_epub/0.1'})
    if r.status_code == 200:
        return url
    elif r.status_code == 303:  # redirect
        return find_url(r.headers['Location'])
    else:
        return None


def find_pmc_url(pmcid):
    # pmcid = pubmed_to_pmc(pmid)
    # if pmcid is not None:
    logger.debug('PMCID: %s', pmcid)
    # Check whether PMC has a pdf
    url = PMC_PDF_URL.format(pmcid=pmcid[3:], toolname=TOOLNAME, email=EMAIL)
    url = find_url(url)
    file_format = 'pdf'
    if url is None:
        url = PMC_ePUB_URL.format(pmcid=pmcid[3:], toolname=TOOLNAME, email=EMAIL)
        url = find_url2(url)
        file_format = 'epub'
    return url, file_format
    # return None

# def pubmed_to_pmc(pmid):
#     url = API_URL.format(pmid=pmid, toolname=TOOLNAME, email=EMAIL)
#     reply = requests.get(url).json()
#     records = reply['records'][0]
#     pmcid = records.get('pmcid', None)
#     return pmcid

def download_pdf(pubmed_csv_dir, save_articles, skiprows, nrows):
    # with open(pubmed_csv_dir, "rt") as f_obj_int, open(pubmed_csv_filtered_dir, 'wt') as f_obj_out:
    with open(pubmed_csv_dir, "rt") as f_obj_int:
        # writer = csv.writer(f_obj_out, dialect='excel')
        pubmed_csv = csv.reader(f_obj_int, dialect='excel')
        pubmed_csv_rows = list(pubmed_csv)
        # print(len(pubmed_csv_rows))
        if nrows is None:
            nrows = len(pubmed_csv_rows) - skiprows
        # print(nrows)
        for i in range(skiprows, skiprows+nrows):
            # print(i)
            pubmed_csv_row = pubmed_csv_rows[i]
            pmid_pmcid = pubmed_csv_row[7]
            article_title = pubmed_csv_row[0]
            print(pmid_pmcid)
            print(article_title)
            if 'PMCID' in pmid_pmcid:
                pmcid = pmid_pmcid[-10:]
                article_url, file_format = find_pmc_url(pmcid)
                if article_url is not None:
                    print(article_url)
                    if 'pdf' in file_format:
                        os.system('wget --user-agent="Mozilla" ' + article_url + ' -O ' + save_articles + pmcid + '.pdf')
                    else:
                        os.system('wget --user-agent="Mozilla" ' + article_url + ' -O ' + save_articles + pmcid + '.epub')
                else:
                    print('No pdf or epub found')
            print('\n')

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-pubmed_csv', help='The csv file created from PubMed')
    parser.add_argument('-save_articles', help='The directry to save the pdf files')
    parser.add_argument('-skiprows',type=int, default=1, help='Skip the some rows in the csv')
    parser.add_argument('-nrows',type=int, default=None, help='Read the rows after skipping')

    # parser.add_argument('-save_csv', help='The directry to save the filtered csv')
    args = parser.parse_args()
    download_pdf(args.pubmed_csv, args.save_articles, args.skiprows, args.nrows)
