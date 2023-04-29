import re
from pprint import pprint

import requests
from bs4 import BeautifulSoup
import pandas


def get_vacancies():
    path = 'https://hh.ru/search/vacancy'
    search = {'text': 'Python'}
    r = requests.get(path, headers={'User-Agent': 'Custom'}, params=search)
    hh_response = r.text
    pre_url_regex = re.compile(r'm.hh.ru/vacancy/(\d+)"},')
    pre_page_regex = re.compile(r'text=Python&amp;page=(\d*)&amp;')
    vacancies_ids = set(pre_url_regex.findall(hh_response))
    pages = max(map(int, pre_page_regex.findall(hh_response)))
    for page in range(1, pages + 1):
        search['page'] = page
        r = requests.get(path, headers={'User-Agent': 'Custom'}, params=search)
        temp_vacancies_id = pre_url_regex.findall(r.text)
        vacancies_ids.update(temp_vacancies_id)
    return vacancies_ids


def get_vacancies_test():
    path = 'https://hh.ru/search/vacancy'
    search = {'text': 'Python'}
    r = requests.get(path, headers={'User-Agent': 'Custom'}, params=search)
    hh_response = r.text
    pre_url_regex = re.compile(r'm.hh.ru/vacancy/(\d+)"},')
    vacancies_ids = set(pre_url_regex.findall(hh_response))
    return vacancies_ids


def get_requirements(id):
    path = f'https://pskov.hh.ru/vacancy/{id}'
    r = requests.get(path, headers={'User-Agent': 'Custom'})
    soup = BeautifulSoup(r.text, 'html.parser')
    vacancy_details = soup.find('div', class_='g-user-content')
    if not vacancy_details:
        return ()
    details_list = [detail.text for detail in vacancy_details.findAll('li')]
    if not details_list:
        details_list = [detail.text for detail in vacancy_details.findAll('p') if detail.text.startswith('•')]
    # if not details_list:
    #     print(id)
    return (details_list, )


def save_to_file():
    pass

if __name__ == '__main__':

    worked_vacancies = {}
    failed_vacancies = []
    vacancies_ids = get_vacancies()
    for vacancy_id in vacancies_ids:
        vacancy_requirements = get_requirements(vacancy_id)
        if vacancy_requirements:
            worked_vacancies[vacancy_id] = vacancy_requirements
        else:
            failed_vacancies.append(vacancy_id)
    print(f'На {len(worked_vacancies)} вакансий с нормальным форматированием пришлось {len(failed_vacancies)} без '
          f'нормального форматирования.')
