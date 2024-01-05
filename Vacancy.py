import re
import requests
from bs4 import BeautifulSoup, NavigableString, Tag

# для валют переписать parse_salary на фабрику функций или вроде того
TAXES = 0.13
COURSES = {
    'USD': 91,
    'KZT': 0.2,
    'руб': 1,
    '₽': 1,
}


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
        soup = BeautifulSoup(r.text, 'lxml')
        # check if there is error in getting page info
        while not soup.find('h1', attrs={'data-qa': 'vacancy-title'}):
            r = requests.get(path, headers={'User-Agent': 'Custom'})
            soup = BeautifulSoup(r.text, 'lxml')
        soup = Vacancy.clearify(soup)
        title = Vacancy.parse_title(soup)
        salary = Vacancy.parse_salary(soup)
        experience = Vacancy.parse_experience(soup)
        key_skills = Vacancy.parse_key_skills(soup)
        detailed_information = Vacancy.parse_detailed_information(soup)
        vacancy = cls(id=id, title=title, salary=salary, experience=experience,
                      detailed_information=detailed_information, key_skills=key_skills)
        return vacancy

    @staticmethod
    def clearify(soup):
        for tag in soup.find_all():
            if len(tag.get_text(strip=True)) == 0:
                tag.replace_with(NavigableString(''))
        return soup

    @staticmethod
    def parse_title(soup):
        return ''.join(soup.find('h1', attrs={'data-qa': 'vacancy-title'}).stripped_strings)

    @staticmethod
    def parse_salary(soup):
        salary = ''.join(soup.find('div', attrs={'data-qa': 'vacancy-salary'}).find('span').stripped_strings)
        salary = salary.replace('\xa0', '')  # заменяем разделитель разряда пустой строкой
        currency_template = r'(' + '|'.join(COURSES.keys()) + ')(.*)'  # собираем шаблон из всех значимых валют
        value_template = re.compile(currency_template)  # компилируем шаблон поиска
        try:
            currency, tax_flag = value_template.findall(salary)[0]  # выполняем поиск, группируем результат
        except IndexError:
            return []

        money_template = re.compile(r'(\d{3,7})')
        salary_delta = list(map(int, money_template.findall(salary))) # переводим все найденные значения в int, формируем список
        for i in range(len(salary_delta)):  # нельзя воспользоваться итератором, надо отредактировать каждое значение в массиве
            if tax_flag == 'до вычета налогов':  # высчитываем налог, чтобы не тешить себя иллюзиями
                salary_delta[i] = round(salary_delta[i] * (1 - TAXES))
            salary_delta[i] = salary_delta[i] * COURSES[currency]
        return salary_delta

    @staticmethod
    def parse_experience(soup):
        return ' '.join(soup.find('span', attrs={'data-qa': 'vacancy-experience'}).stripped_strings)

    @staticmethod
    def parse_key_skills(soup):
        key_skills_block = soup.find('div', class_='bloko-tag-list')
        key_skills = [str(key_skill.string) for key_skill in key_skills_block.find_all('span')] if key_skills_block else []
        return key_skills

    @staticmethod
    def parse_detailed_information(soup):
        vacancy_details = soup.find('div', class_='vacancy-branded-user-content')
        if not vacancy_details:
            vacancy_details = soup.find('div', attrs={'data_qa': 'vacancy_description'})
        if not vacancy_details:
            vacancy_details = soup.find('div', class_='g-user-content')
        return Vacancy.clearify(vacancy_details)
