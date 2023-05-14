import json
import re

import requests
from bs4 import BeautifulSoup

from Vacancy import Vacancy


class HHParser:

    def __init__(self):
        self.search_path = 'https://hh.ru/search/vacancy'
        self.search_params = {'text': 'Python', 'schedule': 'remote', 'salary': '90000', 'page': 1}
        self.pre_url_regex = re.compile(r'm.hh.ru/vacancy/(\d+)"},')
        # self.pre_page_regex = re.compile(r'text=Python&amp;.*page=(\d*)')
        self.vacancy_ids = set()
        self.vacancies = []
        self.key_skills = {}

    def get_vacancy_ids(self):
        request = requests.get(self.search_path, headers={'User-Agent': 'Custom'}, params=self.search_params)
        hh_response = request.text
        ids = set(self.pre_url_regex.findall(hh_response))
        soup = BeautifulSoup(hh_response, 'html.parser')
        pages = max(map(int, [page.find(string=re.compile('\d+')) for page in
                              soup.find_all('a', attrs={'data-qa': 'pager-page'})]))
        for page in range(2, pages + 1):
            self.search_params['page'] = page
            r = requests.get(self.search_path, headers={'User-Agent': 'Custom'}, params=self.search_params)
            ids.update(self.pre_url_regex.findall(r.text))
        return ids

    def get_first_50_vacancie_ids(self):
        request = requests.get(self.search_path, headers={'User-Agent': 'Custom'}, params=self.search_params)
        hh_response = request.text
        ids = set(self.pre_url_regex.findall(hh_response))
        return ids

    def add_vacancy(self, vacancy):
        self.vacancies.append(vacancy)
        self.vacancy_ids.add(vacancy.id)
        for key_skill in vacancy.key_skills:
            if key_skill not in self.key_skills:
                self.key_skills[key_skill] = 1
            else:
                self.key_skills[key_skill] += 1

    def save_vacancies_to_json(self):
        with open('hhparser.json', 'w') as fp:
            for vacancy in self.vacancies:
                json.dump(vacancy.to_dict(), fp)
                fp.write('\n')
            # encoded_vacancies = jsonpickle.encode(self.vacancies, unpicklable=False, max_depth=2)
            # fp.write(encoded_vacancies)
            # fp.flush()

    def load_vacancies_from_json(self):
        with open('hhparser.json', 'r') as fp:
            json_line = fp.readline()
            while json_line:
                obj_dict = json.loads(json_line)
                self.add_vacancy(Vacancy.from_dict(obj_dict))
                json_line = fp.readline()

            # decoded_data = jsonpickle.decode(data)
            # for vacancy_dict in decoded_data:
            #     # print(vacancy_dict.keys())
            #     # print(vacancy_dict.values())
            #     # vacancy_dict['id'] = json.loads(vacancy_dict['id'])
            #     # vacancy_dict['title'] = json.loads(vacancy_dict['title'])
            #     # vacancy_dict['salary'] = json.loads(vacancy_dict['salary'] )
            #     print(vacancy_dict['detailed_information'])
            #     vacancy_dict['detailed_information'] = json.loads(vacancy_dict['detailed_information'])
            #     # vacancy_dict['key_skills'] = json.loads(vacancy_dict['key_skills'])
            #
            #     self.add_vacancy(Vacancy.create_vacancy_from_dict(vacancy_dict))
