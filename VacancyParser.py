import re

from bs4 import NavigableString


# для валют переписать parse_salary на фабрику функций или вроде того
TAXES = 0.13
COURSES = {
    'USD': 94.15,
    'KZT': 0.21,
    'руб': 1,
    '₽': 1,
    '$': 94.15,
    '€': 100.08,
    '': 1
}


class VacancyParser:

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
        salary_tag = soup.find('div', attrs={'data-qa': 'vacancy-salary'})
        if not salary_tag:
            return []
        salary = ''.join(salary_tag.find('span').stripped_strings)
        salary = salary.replace('\xa0', '')  # заменяем разделитель разряда пустой строкой
        currency_template = r'(' + '|'.join(COURSES.keys()) + ')(.*)'  # собираем шаблон из всех значимых валют
        value_template = re.compile(currency_template)  # компилируем шаблон поиска
        try:
            currency, tax_flag = value_template.findall(salary)[0]  # выполняем поиск, группируем результат
        except IndexError:
            return []

        money_template = re.compile(r'(\d{3,7})')
        max_salary = max(map(int, money_template.findall(salary))) # переводим все найденные значения в int, формируем список
        if tax_flag == 'до вычета налогов':  # высчитываем налог, чтобы не тешить себя иллюзиями
            max_salary = round(max_salary * (1 - TAXES))
        max_salary = max_salary * COURSES[currency]
        return max_salary

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
        return VacancyParser.clearify(vacancy_details)
