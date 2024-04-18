import unittest
from Vacancy import Vacancy
import requests
from bs4 import BeautifulSoup


class TestHHParser(unittest.TestCase):

    def setUp(self):
        path = f'https://hh.ru/vacancy/97125918'
        r = requests.get(path, headers={'User-Agent': 'Custom'})
        soup = BeautifulSoup(r.text, 'lxml')
        while not soup.find('h1', attrs={'data-qa': 'vacancy-title'}):
            r = requests.get(path, headers={'User-Agent': 'Custom'})
            soup = BeautifulSoup(r.text, 'lxml')
        self.soup = soup

    def test_parse_title(self):
        title = Vacancy.parse_title(self.soup)
        self.assertEqual(title, 'Аналитик данных SQL (Middle)')

    def test_parse_salary(self):
        salary = Vacancy.parse_salary(self.soup)
        self.assertEqual(salary, [70000, 140000])

    def test_parse_experience(self):
        experience = Vacancy.parse_experience(self.soup)
        self.assertEqual(experience, '1–3 года')

    def test_parse_key_skills(self):
        key_skills = Vacancy.parse_key_skills(self.soup)
        self.assertEqual(key_skills, ['Английский язык', 'Transact-SQL', 'Оптимизация запросов', 'MySQL', 'SQL',
                                      'Базы данных', 'MS SQL'])

    def test_parse_detailed_information(self):
        detailed_information = Vacancy.parse_detailed_information(self.soup)
        self.assertNotEqual(detailed_information, '')

    def test_vacancy_create_from_id(self):
        test_vacancy = Vacancy.create_vacancy_from_id('97125918')
        self.assertEqual(test_vacancy, '97125918 Аналитик данных SQL (Middle)')


unittest.main()
