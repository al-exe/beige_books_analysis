from bs4 import BeautifulSoup as bs
import requests
import sys

ARCHIVE_URL = "https://www.federalreserve.gov/monetarypolicy/beige-book-archive.htm"

YEAR_PRE_URL = "https://www.federalreserve.gov"
YEAR_IDENTIFIER_1 = "/monetarypolicy/beigebook"
YEAR_IDENTIFIER_2 = "https://www.federalreserve.gov/monetarypolicy/beigebook/beigebook"
YEAR_IDENTIFIER_3 = "https://www.federalreserve.gov/fomc/beigebook"

YI1_LEN = len(YEAR_IDENTIFIER_1)
YI2_LEN = len(YEAR_IDENTIFIER_2)
YI3_LEN = len(YEAR_IDENTIFIER_3)

SCRAPING_DIRECTORY = "./scraped_files/"

# TODO: Add comprehensive comments
# TODO: Clean up repetitive or messy code


def main():
    err_print("Extracting archive...")
    archive = soupify(ARCHIVE_URL)
    err_print("Extracting yearly archives...")
    years = grab_websites(archive, YEAR_PRE_URL, year_id_check)
    reports = []
    err_print("Extracting quarterly reports...")
    for year in years:
        yearly_reports = grab_websites(soupify(year), YEAR_PRE_URL, year_id_check)
        reports.extend(yearly_reports)
    err_print("Removing .pdf files...")
    clean(reports, ".pdf")
    count = 0
    err_print("Saving reports to directory...")
    for report in reports:
        save(soupify(report).prettify(), str(count))
        count += 1
    err_print("Scraping complete!")


def soupify(url):
    raw_html = requests.get(url).content
    return bs(raw_html, 'html.parser')


def grab_websites(html_soup, pre_url="", conditional=lambda l: int(l[:4] == 'http')):
    links = html_soup.find_all("a")
    htmls = []
    for link in links:
        proto_link = str(link.get('href'))
        condition = conditional(proto_link)
        if condition == 1:
            full_link = pre_url + proto_link
            htmls.append(full_link)
            err_print("Grabbed " + full_link + "!")
        elif condition > 1:
            htmls.append(proto_link)
            err_print("Grabbed " + proto_link + "!")
    return htmls


def clean(sites, unwanted_type):
    for site in sites:
        if site[-len(unwanted_type):] == unwanted_type:
            sites.remove(site)


def save(contents, name):
    new_file = open(SCRAPING_DIRECTORY + name + '.html', 'w')
    new_file.write(contents)
    new_file.close()
    err_print("Saving report as " + name + ".html...")


def year_id_check(link):
    if link[:YI1_LEN] == YEAR_IDENTIFIER_1:
        return 1
    elif link[:YI2_LEN] == YEAR_IDENTIFIER_2:
        return 2
    elif link[:YI3_LEN] == YEAR_IDENTIFIER_3:
        return 3
    else:
        return 0


def err_print(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

if __name__ == "__main__":
    main()
