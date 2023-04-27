import re

import requests

if __name__ == '__main__':
    path = 'https://hh.ru/search/vacancy'
    search = {'text': 'Python'}
    r = requests.get(path, headers={'User-Agent': 'Custom'}, params=search)
    # print(r.url)
    # print(r.text)
    hh_response = r.text
    pre_url_regex = re.compile(r'm.hh.ru/vacancy/(\d+)"},')
    pre_page_regex = re.compile(r'text=Python&amp;page=(\d*)&amp;')
    vacancies_ids = set(pre_url_regex.findall(hh_response))
    pages = max(map(int, pre_page_regex.findall(hh_response)))
    for page in range(1, pages+1):
        search['page'] = page
        r = requests.get(path, headers={'User-Agent': 'Custom'}, params=search)
        temp_vacancies_id = pre_url_regex.findall(r.text)
        vacancies_ids.update(temp_vacancies_id)
    print(vacancies_ids)
    print(pages)
