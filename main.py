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


def get_vacancy_user_part(id):
    path = f'https://pskov.hh.ru/vacancy/{id}'
    r = requests.get(path, headers={'User-Agent': 'Custom'})
    soup = BeautifulSoup(r.text, 'html.parser')
    vacancy_details = soup.find('div', class_="tmpl_hh_wrapper")
    if not vacancy_details:
        vacancy_details = soup.find('div', attrs={'data_qa': 'vacancy_description'})
    if not vacancy_details:
        vacancy_details = soup.find('div', class_='g-user-content')
    return vacancy_details


def get_requirements_from_page_part(page_part):
    details_list = [detail.text for detail in page_part.findAll('li')]
    list_points = ('•', '-', '—')
    if not details_list:
        details_list = [detail.text for detail in page_part.findAll('p') if detail.text.startswith(list_points)]
    if not details_list:
        # print(page_part)
        return []
    return details_list


if __name__ == '__main__':

    worked_vacancies = {}
    failed_vacancies = []
    vacancies_ids = get_vacancies()
    vacancies_user_parts = {}
    requirements = {}
    tmp_file = open('crazy_list.html', 'w', errors='replace')
    for vacancy_id in vacancies_ids:
        vacancy_user_part = get_vacancy_user_part(vacancy_id)
        requirement = get_requirements_from_page_part(vacancy_user_part)
        vacancies_user_parts[vacancy_id] = vacancy_user_part
        requirements[vacancy_id] = requirement
        print(f'<h2>{vacancy_id}</h2>', file=tmp_file)
        print(vacancy_user_part, file=tmp_file)
    tmp_file.close()
    #     if vacancy_user_part:
    #         worked_vacancies[vacancy_id] = vacancy_user_part
    #     else:
    #         failed_vacancies.append(vacancy_id)
    # print(f'На {len(worked_vacancies)} вакансий с нормальным форматированием пришлось {len(failed_vacancies)} без '
    #       f'нормального форматирования.')
    # print('Без форматирования: ', failed_vacancies)
    #
    # with open('crazy_list.html', 'w') as temp_file:
    #     for key, value in vacancies_user_parts.items():
    #         temp_file.write(str(key))
    #         temp_file.write(str(value, errors='replace'))
