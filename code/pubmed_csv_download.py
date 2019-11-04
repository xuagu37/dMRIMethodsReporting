import requests
import csv
import os
import xml.etree.ElementTree as ET

def save_xml(pmcid, save_files):
    oa_url = 'https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id=' + pmcid
    response = requests.get(oa_url)
    root = ET.fromstring(response.text)
    tree = ET.ElementTree(root)
    save_dir = save_files + 'xml/'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    tree.write(save_dir + pmcid + '.xml')

def get_download_url(pmcid):
    oa_url = 'https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id=' + pmcid
    response = requests.get(oa_url)
    oa_xml = response.text
    tar_url = oa_xml[oa_xml.find('ftp'):oa_xml.find('.tar.gz')+7]
    pdf_url = oa_xml[oa_xml.rfind('ftp'):oa_xml.find('.pdf')+4]
    return tar_url, pdf_url

def download_articles(pubmed_csv_dir, save_files, skiprows, nrows):
    save_tar_dir = save_files + 'tar/'
    if not os.path.exists(save_tar_dir):
        os.makedirs(save_tar_dir)
    save_pdf_dir = save_files + 'pdf/'
    if not os.path.exists(save_pdf_dir):
        os.makedirs(save_pdf_dir)
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
                save_xml(pmcid, save_files)
                tar_url, pdf_url = get_download_url(pmcid)
                if tar_url != '':
                    print(tar_url)
                    os.system('wget --user-agent="Mozilla" ' + tar_url + ' -O ' + save_tar_dir + pmcid + '.tar.gz --quiet &')
                else:
                    print('No tar found!')
                if pdf_url != '':
                    print(pdf_url)
                    os.system('wget --user-agent="Mozilla" ' + pdf_url + ' -O ' + save_pdf_dir + pmcid + '.pdf --quiet &')
                else:
                    print('No pdf found!')
            print('\n')

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-pubmed_csv', help='The csv file created from PubMed')
    parser.add_argument('-save_files', help='The directry to save the articles')
    parser.add_argument('-skiprows',type=int, default=1, help='Skip the some rows in the csv')
    parser.add_argument('-nrows',type=int, default=None, help='Read the rows after skipping')

    # parser.add_argument('-save_csv', help='The directry to save the filtered csv')
    args = parser.parse_args()
    download_articles(args.pubmed_csv, args.save_files, args.skiprows, args.nrows)
