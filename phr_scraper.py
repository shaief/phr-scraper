import requests
from bs4 import BeautifulSoup
import csv

phr_base_url = 'http://phr.org.il/'
wanted_number_of_articles = 2
wanted_pages = [5, 7, 8, 9, 10, 361]  # relevant page numbers - check the links on website

header = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0) Gecko/20100101 Firefox/32.0', }


def scrape_department_page(page):
    '''
    This function scrapes department's page articles headers and returns department name and lists of titles,
    dates and links of articles.
    :param page: page number as appears in the website
    :return: department name and lists of titles, dates and links of articles.
    '''
    wanted_page = '{}{}{}'.format(phr_base_url, 'default.asp?PageID=', page)
    r = requests.get(wanted_page, headers=header)
    soup = BeautifulSoup(r.content)
    department_from_title = soup.title.string
    print('Now working on page {}: {}'.format(page, department_from_title))
    articles = {}
    soup_titles = soup.find_all('td', class_='Title')
    soup_dates = soup.find_all('td', class_='Date')
    soup_links = soup.find_all('a', class_='Continue3')

    return department_from_title, soup_titles, soup_dates, soup_links


def scrape_articles_data(soup_titles, soup_dates, soup_links):
    '''
    This function scrapes data of each article and organises it into a dictionary of dictionaries.
    :param soup_titles: a list of all article titles of a page as <class 'bs4.element.Tag'>
    :param soup_dates: a list of all article dates of a page as <class 'bs4.element.Tag'>
    :param soup_links: a list of all article links of a page as <class 'bs4.element.Tag'>
    :return: articles: a dictionary of dictionaries contains strings of article's data
    '''
    articles = {}
    for i, title in enumerate(soup_titles):
        if i > wanted_number_of_articles:
            break
        articles[i] = {}
        articles[i]['title'] = title.contents[0]
        articles[i]['date'] = soup_dates[i].contents[0]
        # print('getting this link: {}'.format(soup_links[i]['href']))
        articles[i]['link'] = soup_links[i]['href']
        wanted_article = '{}{}'.format(phr_base_url, soup_links[i]['href'])
        article_request = requests.get(wanted_article, headers=header)
        article_soup = BeautifulSoup(article_request.content)
        article_main_content = article_soup.find('td', attrs={'width': 441}).get_text()  # .strip('\n')
        articles[i]['content'] = article_main_content
    return articles


def save_to_csv(page, department_from_title, articles):
    '''
    Saves each page's articles to a CSV file with page number in its name.
    :param page: page number as appears in the website.
    :param department_from_title: department name string
    :param articles: a dictionary of dictionaries.
    :return: nothing
    '''
    with open(file='./phr-data/test_{}{}'.format(page, '.csv'), mode='w', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)

        writer.writerow(['department name from title ==> post_tag',
                         'article title ==> post_title',
                         'date published ==> post_date',
                         'article link ==> post_excerpt'
                         'article + headers ==> post_content'])

        for k, v in articles.items():
            if 'content' in v:
                writer.writerow([department_from_title,
                                 v['title'],
                                 v['date'],
                                 '{}{}'.format(phr_base_url, v['link']),
                                 '{}\n{}\n{}'.format(department_from_title, v['date'], v['content'])])
        print("Done saving page {}'s articles: {}".format(page, department_from_title))


if __name__ == '__main__':
    for page in wanted_pages:
        department_from_title, titles, dates, links = scrape_department_page(page)
        articles = scrape_articles_data(titles, dates, links)
        save_to_csv(page, department_from_title, articles)

    print('Finished running script! check your CSV files...')
