from HHParser import HHParser
from Vacancy import Vacancy

if __name__ == '__main__':
    hh_parser = HHParser()
    vacancies_ids = hh_parser.get_vacancies_ids()
    for vacancy_id in vacancies_ids:
        vacancy = Vacancy.create_vacancy_from_id(vacancy_id)
        hh_parser.add_vacancy(vacancy)
        key_skills = vacancy.key_skills
        for key_skill in key_skills:
            if key_skill not in hh_parser.key_skills:
                hh_parser.key_skills[key_skill] = 1
            else:
                hh_parser.key_skills[key_skill] += 1
        print(vacancy_id, vacancy.title, vacancy.salary, vacancy.key_skills)
