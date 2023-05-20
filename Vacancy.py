import re
import requests
from bs4 import BeautifulSoup, NavigableString, Tag


TAXES = 0.13
USD_COURSE = 80

class Vacancy:

    def __init__(self, id, title, salary, experience, detailed_information, key_skills):
        self.id = id
        self.title = title
        self.salary = salary
        self.experience = experience
        self.detailed_information = detailed_information
        self.key_skills = key_skills

    def __str__(self):
        return f'{str(self.id)} {str(self.title)}'

    def to_dict(self):
        vacancy_dict = {'id': self.id, 'title': self.title, 'salary': self.salary, 'experience': self.experience,
                        'detailed_information': self.detailed_information, 'key_skills': self.key_skills}
        return vacancy_dict

    @classmethod
    def from_dict(cls, vacancy_dict):
        vacancy = cls(id=vacancy_dict['id'],
                      title=vacancy_dict['title'],
                      salary=vacancy_dict['salary'],
                      experience=vacancy_dict['experience'],
                      detailed_information=vacancy_dict['detailed_information'],
                      key_skills=vacancy_dict['key_skills'])
        return vacancy

    def __repr__(self):
        return self.__dict__

    @classmethod
    def create_vacancy_from_id(cls, id):
        path = f'https://hh.ru/vacancy/{id}'
        r = requests.get(path, headers={'User-Agent': 'Custom'})
        fp = open('tmp_hh.html', 'w', errors='ignore')
        fp.write(r.text)
        soup = BeautifulSoup(r.text, 'lxml')
        # check if there is error in getting page info
        while not soup.find('h1', attrs={'data-qa': 'vacancy-title'}):
            r = requests.get(path, headers={'User-Agent': 'Custom'})
            soup = BeautifulSoup(r.text, 'lxml')
            soup.find('h1', attrs={'data-qa': 'vacancy-title'})
        fp.write(soup.text)
        fp.close()
        title = ' '.join(soup.find('h1', attrs={'data-qa': 'vacancy-title'}).stripped_strings)
        salary = ' '.join(soup.find('div', attrs={'data-qa': 'vacancy-salary'}).find('span').stripped_strings)
        # salary = cls.parse_salary(salary)
        experience = ' '.join(soup.find('span', attrs={'data-qa': 'vacancy-experience'}).stripped_strings)
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
        vacancy = cls(id=id, title=title, salary=salary, experience=experience,
                      detailed_information=detailed_information, key_skills=key_skills)
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
        value_template = re.compile(r'[USD|руб].*')
        if salary.endswith('не указана'):
            return None
        value = value_template.search(salary).group()

        salary = salary.replace('\xa0', '')
        money_template = re.compile(r'(\d{3,7})')
        salary_delta = list(map(int, money_template.findall(salary)))

        if value.endswith('до вычета налогов'):
            for i in range(len(salary_delta)):
                salary_delta[i] = round(salary_delta[i] * (1-TAXES))
            value = value.replace('до вычета налогов', 'на руки')

        if 'USD' in value:
            for i in range(len(salary_delta)):
                salary_delta[i] = salary_delta[i] * USD_COURSE
            value = value.replace('USD', 'руб.')

        return salary_delta, value

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