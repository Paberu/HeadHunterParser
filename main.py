import re

import requests
from bs4 import BeautifulSoup


def get_vacancies_ids():
    path = 'https://hh.ru/search/vacancy'
    search = {'text': 'Python', 'schedule': 'remote', 'salary': '90000'}
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


def get_first_50_vacancies_ids():
    path = 'https://hh.ru/search/vacancy'
    search = {'text': 'Python', 'schedule': 'remote', 'salary': '90000'}
    r = requests.get(path, headers={'User-Agent': 'Custom'}, params=search)
    hh_response = r.text
    pre_url_regex = re.compile(r'm.hh.ru/vacancy/(\d+)"},')
    vacancies_ids = set(pre_url_regex.findall(hh_response))
    return vacancies_ids


def get_looked_for_page_part(id):
    path = f'https://pskov.hh.ru/vacancy/{id}'
    r = requests.get(path, headers={'User-Agent': 'Custom'})
    soup = BeautifulSoup(r.text, 'html.parser')
    vacancy_details = soup.find('div', class_='tmpl_hh_wrapper')
    if not vacancy_details:
        vacancy_details = soup.find('div', attrs={'data_qa': 'vacancy_description'})
    if not vacancy_details:
        vacancy_details = soup.find('div', class_='g-user-content')
    return vacancy_details


def parse_looked_for_page_part(page_part):
    user_content = page_part.find('div', class_='vacancy-branded-user-content')
    if not user_content:
        user_content = page_part
    current_key = BeautifulSoup('<strong></strong>', 'html.parser').strong  # костыль для создания ключа с пустой строкой и тэгом strong
    user_content_keys = []
    user_content_parts = {}
    for tag in user_content.descendants:
        if tag.name == 'strong':
            user_content_keys.append(tag)
            current_key = tag
        elif tag.name == 'ul':
            user_content_parts[current_key] = tag
    if len(user_content_keys) != len(user_content_parts.keys()):
        for key in user_content_keys:
            if key not in user_content_parts.keys():
                user_content_parts[key] = key.parent
    return user_content_parts


def detag(parts):
    detagged_parts = {}
    for key, value in parts.items():
        if value.name == 'ul':
            detagged_parts[key.string] = [detail.text for detail in value.findAll('li')]
        else:
            detagged_parts[key.string] = value.string
    return detagged_parts


if __name__ == '__main__':
    vacancies_ids = get_first_50_vacancies_ids()
    vacancies_user_parts = {}
    requirements = {}
    tmp_file = open('crazy_list.html', 'w', errors='replace')
    tmplt_hh_file = open('tmplt_hh.html', 'w', errors='replace')
    for vacancy_id in vacancies_ids:
        vacancy_user_part = get_looked_for_page_part(vacancy_id)
        # requirement = parse_looked_for_page_part(vacancy_user_part)
        vacancies_user_parts[vacancy_id] = vacancy_user_part
        # requirements[vacancy_id] = requirement
        print(f'<h2>{vacancy_id}</h2>', file=tmp_file)
        print(vacancy_user_part, file=tmp_file)
        if vacancy_user_part.attrs['class'] == ['tmpl_hh_wrapper']:
            print(f'<h2>{vacancy_id}</h2>', file=tmplt_hh_file)
            print(vacancy_user_part, file=tmplt_hh_file)
            print(detag(parse_looked_for_page_part(vacancy_user_part)))
    tmp_file.close()
    tmplt_hh_file.close()
