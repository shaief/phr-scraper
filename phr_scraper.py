import requests
from bs4 import BeautifulSoup
import csv

phr_base_url = 'http://phr.org.il/'

wanted_number_of_articles = 1000

wanted_pages = [5, 7, 8, 9, 10, 361]  # relevant page numbers

header = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0) Gecko/20100101 Firefox/32.0', }
for page in wanted_pages:
    wanted_page = '{}{}{}'.format(phr_base_url, 'default.asp?PageID=', page)
    r = requests.get(wanted_page, headers=header)
    soup = BeautifulSoup(r.content)
    department_from_title = soup.title.string
    print('Now working on: {}'.format(department_from_title))
    body = soup.name
    counter = [0, 0, 0]
    articles = {}
    for i, title in enumerate(soup.find_all('td', class_='Title')):
        counter[0] += 1
        if counter[0] > wanted_number_of_articles:
            break
        articles[i] = {}
        articles[i]['title'] = title.contents[0]
    for i, date in enumerate(soup.find_all('td', class_='Date')):
        counter[1] += 1
        if counter[1] > wanted_number_of_articles:
            break
        articles[i]['date'] = date.contents[0]
    for i, link in enumerate(soup.find_all('a', class_='Continue3')):
        counter[2] += 1
        if counter[2] > wanted_number_of_articles:
            break
        # print('getting link! {}'.format(link['href']))
        articles[i]['link'] = link['href']
        wanted_article = '{}{}'.format(phr_base_url, link['href'])
        article_request = requests.get(wanted_article, headers=header)
        article_soup = BeautifulSoup(article_request.content)
        article_main_content = article_soup.find('td', attrs={'width': 441}).get_text().strip('\n')
        articles[i]['content'] = article_main_content

    with open(file='./phr-data/{}{}'.format(page, '.csv'), mode='w', encoding='utf-8') as csvfile:
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
print('finished running script! check your CSV files...')