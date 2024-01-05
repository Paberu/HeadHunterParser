import json
import re

import requests
from bs4 import BeautifulSoup

from Vacancy import Vacancy


def translate_key_skills_dict_to_list(key_skills_dict):
    sorted_key_skills = sorted(key_skills_dict.items(), key=lambda x: x[1], reverse=True)
    return [f'{skill[0]} - {skill[1]}' for skill in sorted_key_skills]


class HHParser:

    def __init__(self, search, schedule):
        self.search_path = 'https://hh.ru/search/vacancy'
        self.search_params = {'text': search, 'page': 1}
        if schedule:
            self.search_params['schedule'] = schedule
        self.pre_url_regex = re.compile(r'm.hh.ru/vacancy/(\d+)"},')
        self.vacancy_ids = set()
        self.vacancies = []
        self.key_skills = {}
        self.experience = {'не требуется': 0, '1–3 года': 0, '3–6 лет': 0, 'более 6 лет': 0}
        self.salaries = []

    def _get_vacancy_ids(self):
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

    def _get_first_50_vacancie_ids(self):
        request = requests.get(self.search_path, headers={'User-Agent': 'Custom'}, params=self.search_params)
        hh_response = request.text
        ids = set(self.pre_url_regex.findall(hh_response))
        return ids

    def get_vacancies(self):
        ids = self._get_first_50_vacancie_ids()
        # ids = {'79582780', }
        for vacancy_id in ids:
            if vacancy_id not in self.vacancy_ids:
                vacancy = Vacancy.create_vacancy_from_id(vacancy_id)
                self.add_vacancy(vacancy)

    def add_vacancy(self, vacancy):
        self.vacancies.append(vacancy)
        self.vacancy_ids.add(vacancy.id)
        for key_skill in vacancy.key_skills:
            if key_skill not in self.key_skills:
                self.key_skills[key_skill] = 1
            else:
                self.key_skills[key_skill] += 1
        self.experience[vacancy.experience] += 1

    def split_vacancies_by_salary(self):
        salary_not_set = 0
        salary_too_big = 0
        salary_steps = {}
        salary_step = 40000
        for i in range(1, 11):
            salary_steps[i * salary_step] = 0

        for vacancy in self.vacancies:
            if vacancy.salary:
                for salary in vacancy.salary:
                    for key in salary_steps.keys():
                        if salary < key:
                            salary_steps[key] += 1
                            break
                    else:
                        salary_too_big += 1
            else:
                salary_not_set += 1

        salary_list = []
        salary_list.append(f'З/п не указана - {salary_not_set}')
        previous_step = 0
        for salary_step, count in salary_steps.items():
            salary_list.append(f'З/п от {previous_step} до {salary_step} - {count}')
            previous_step = salary_step
        salary_list.append(f'З/п выше, чем {salary_step} - {salary_too_big}')

        self.salaries = salary_list

    def filter_vacancies_by_salary(self, lowest_salary, highest_salary):
        filtered_vacancies = []
        filtered_vacancies_experience = {'не требуется': 0, '1–3 года': 0, '3–6 лет': 0, 'более 6 лет': 0}
        for vacancy in self.vacancies:
            if lowest_salary == highest_salary == 0:
                if not vacancy.salary:
                    if vacancy not in filtered_vacancies:
                        filtered_vacancies.append(vacancy)
                        filtered_vacancies_experience[vacancy.experience] += 1
            else:
                for salary_part in vacancy.salary:
                    if lowest_salary < salary_part < highest_salary:
                        if vacancy not in filtered_vacancies:
                            filtered_vacancies.append(vacancy)
                            filtered_vacancies_experience[vacancy.experience] += 1
                            continue

        self.vacancies_filtered_by_experience_and_salaries = []
        self.key_skills_filtered_by_experience_and_salaries = []
        self.vacancies_filtered_by_salaries = filtered_vacancies
        self.experience_filtered_by_salaries = filtered_vacancies_experience

    def sort_key_skills(self):
        translate_key_skills_dict_to_list(self.key_skills)

    def save_vacancies_to_json(self):
        with open('hhparser.json', 'w') as fp:
            for vacancy in self.vacancies:
                json.dump(vacancy.to_dict(), fp)
                fp.write('\n')

    def load_vacancies_from_json(self):
        with open('hhparser.json', 'r') as fp:
            json_line = fp.readline()
            while json_line:
                obj_dict = json.loads(json_line)
                self.add_vacancy(Vacancy.from_dict(obj_dict))
                json_line = fp.readline()
