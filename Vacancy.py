import requests
from bs4 import BeautifulSoup

from VacancyParser import VacancyParser


class Vacancy(VacancyParser):

    def __init__(self, id, title, salary, experience, detailed_information, key_skills):
        self.id = id
        self.title = title
        self.salary = salary
        self.experience = experience
        self.detailed_information = detailed_information
        self.key_skills = key_skills

    def __str__(self):
        return f'{str(self.id)} {str(self.title)}'

    def __repr__(self):
        return self.__dict__

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

    @classmethod
    def create_vacancy_from_id(cls, id):
        path = f'https://hh.ru/vacancy/{id}'
        r = requests.get(path, headers={'User-Agent': 'Custom'})
        soup = BeautifulSoup(r.text, 'lxml')
        # check if there is error in getting page info
        while not soup.find('h1', attrs={'data-qa': 'vacancy-title'}):
            r = requests.get(path, headers={'User-Agent': 'Custom'})
            soup = BeautifulSoup(r.text, 'lxml')
        title = cls.parse_title(soup)
        salary = cls.parse_salary(soup)
        experience = cls.parse_experience(soup)
        key_skills = cls.parse_key_skills(soup)
        detailed_information = cls.parse_detailed_information(soup)
        vacancy = cls(id=id, title=title, salary=salary, experience=experience,
                      detailed_information=detailed_information, key_skills=key_skills)
        return vacancy

    @classmethod
    def save_vacancy_to_file(cls, id):
        path = f'https://hh.ru/vacancy/{id}'
        r = requests.get(path, headers={'User-Agent': 'Custom'})

        soup = BeautifulSoup(r.text, 'lxml')
        # check if there is error in getting page info
        while not soup.find('h1', attrs={'data-qa': 'vacancy-title'}):
            r = requests.get(path, headers={'User-Agent': 'Custom'})
            soup = BeautifulSoup(r.text, 'lxml')

        with open(f"{id}.html", "w", encoding="utf-8") as file:
            file.write(str(soup))
