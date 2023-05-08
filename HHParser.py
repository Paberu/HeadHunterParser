import re

import requests
from bs4 import BeautifulSoup


class HHParser:

    def __init__(self):
        self.search_path = 'https://hh.ru/search/vacancy'
        self.search_params = {'text': 'Python', 'schedule': 'remote', 'salary': '90000', 'page': 1}
        self.pre_url_regex = re.compile(r'm.hh.ru/vacancy/(\d+)"},')
        # self.pre_page_regex = re.compile(r'text=Python&amp;.*page=(\d*)')
        self.vacancies = []
        self.key_skills = {}

    def get_vacancies_ids(self):
        request = requests.get(self.search_path, headers={'User-Agent': 'Custom'}, params=self.search_params)
        hh_response = request.text
        vacancies_ids = set(self.pre_url_regex.findall(hh_response))
        soup = BeautifulSoup(hh_response, 'html.parser')
        pages = max(map(int, [page.find(string=re.compile('\d+')) for page in
                              soup.find_all('a', attrs={'data-qa': 'pager-page'})]))
        for page in range(2, pages + 1):
            self.search_params['page'] = page
            r = requests.get(self.search_path, headers={'User-Agent': 'Custom'}, params=self.search_params)
            print(r.request.url)
            temp_vacancies_id = self.pre_url_regex.findall(r.text)
            vacancies_ids.update(temp_vacancies_id)
        return vacancies_ids

    def get_first_50_vacancies_ids(self):
        request = requests.get(self.search_path, headers={'User-Agent': 'Custom'}, params=self.search_params)
        hh_response = request.text
        vacancies_ids = set(self.pre_url_regex.findall(hh_response))
        return vacancies_ids

    def add_vacancy(self, vacancy):
        self.vacancies.append(vacancy)
