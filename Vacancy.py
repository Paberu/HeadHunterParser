import re

import requests
from bs4 import BeautifulSoup, NavigableString, Tag


class Vacancy:

    def __init__(self, id, title, salary, detailed_information, key_skills):
        self.id = id
        self.title = title
        self.salary = salary
        self.detailed_information = detailed_information
        self.key_skills = key_skills

    def __str__(self):
        return str(self.id) + str(self.title) + str(self.salary) + str(self.detailed_information) + str(self.key_skills)

    def to_dict(self):
        vacancy_dict = {'id': self.id, 'title': self.title, 'salary': self.salary,
                        'detailed_information': self.detailed_information, 'key_skills': self.key_skills}
        return vacancy_dict

    @classmethod
    def from_dict(cls, vacancy_dict):
        vacancy = cls(id=vacancy_dict['id'],
                      title=vacancy_dict['title'],
                      salary=vacancy_dict['salary'],
                      detailed_information=vacancy_dict['detailed_information'],
                      key_skills=vacancy_dict['key_skills'])
        return vacancy

    def __repr__(self):
        return self.__dict__

    @classmethod
    def create_vacancy_from_id(cls, id):
        path = f'https://hh.ru/vacancy/{id}'
        r = requests.get(path, headers={'User-Agent': 'Custom'})
        soup = BeautifulSoup(r.text, 'html.parser')
        title = ' '.join(soup.find('h1', attrs={'data-qa': 'vacancy-title'}).stripped_strings)
        salary = ' '.join(soup.find('div', attrs={'data-qa': 'vacancy-salary'}).find('span').stripped_strings)
        salary = cls.parse_salary(salary)
        key_skills = []
        key_skills_block = soup.find('div', class_='bloko-tag-list')
        if key_skills_block:
            key_skills = [str(key_skill.string) for key_skill in key_skills_block.find_all('span')]
        vacancy_details = soup.find('div', class_='vacancy-branded-user-content')
        if not vacancy_details:
            vacancy_details = soup.find('div', attrs={'data_qa': 'vacancy_description'})
        if not vacancy_details:
            vacancy_details = soup.find('div', class_='g-user-content')
        detailed_information = cls.clearify(vacancy_details)
        vacancy = cls(id=id, title=title, salary=salary, detailed_information=detailed_information,
                      key_skills=key_skills)
        vacancy.parse_detailed_information()
        return vacancy

    def parse_detailed_information(self):
        # list_points = ('•', '-', '—')
        current_key = BeautifulSoup('<strong></strong>',
                                    'html.parser').strong  # костыль для создания ключа с пустой строкой и тэгом strong
        user_content_keys = []
        user_content_parts = {}
        for tag in self.detailed_information.descendants:
            if tag.name == 'strong':
                user_content_keys.append(tag)
                current_key = tag
            elif tag.name == 'ul':
                user_content_parts[current_key] = tag
        if len(user_content_keys) != len(user_content_parts.keys()):
            for key in user_content_keys:
                if key not in user_content_parts.keys():
                    if key.string != key.parent.string:
                        user_content_parts[key] = key.parent
                    else:
                        start_crazy_search = key.parent
                        next_tag = start_crazy_search.find_next_sibling()
                        complex_value = []
                        while True:
                            if not next_tag:
                                break
                            for child in next_tag.children:
                                if isinstance(child, Tag) and child.name == 'strong':
                                    break
                            else:
                                complex_value.append(next_tag)
                                next_tag = next_tag.find_next_sibling()
                                continue
                            break
                        user_content_parts[key] = complex_value
        self.detailed_information = self.detag(user_content_parts)

    @staticmethod
    def clearify(soup):
        for tag in soup.find_all():
            if len(tag.get_text(strip=True)) == 0:
                tag.replace_with(NavigableString(''))
        return soup

    @staticmethod
    def parse_salary(salary):
        money_template = re.compile(r'(\d{1,3}).(\d{3})')
        country = re.compile(r'[USD|руб].*')
        if not salary.endswith('не указана'):
            salary_delta = []
            value = country.findall(salary)
            for money_tuple in money_template.findall(salary):
                salary_delta.append(int(''.join(d for d in money_tuple)))
            return salary_delta, value
        return None

    @staticmethod
    def detag(parts):
        detagged_parts = {}
        for key, value in parts.items():
            if isinstance(value, list):  # list of Tags by crazy_search
                detagged_list = []
                for part in value:
                    detagged_list.append(part.text)
                detagged_parts[key.string] = detagged_list
            else:  # instance is Tag
                if value.name == 'ul':
                    detagged_parts[key.string] = [detail.text for detail in value.findAll('li')]
                else:
                    detagged_parts[key.string] = ' '.join(value.strings)
            # print(key, type(key), type(value))
        return detagged_parts
