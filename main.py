from HHParser import HHParser
from Vacancy import Vacancy

if __name__ == '__main__':
    hh_parser = HHParser()
    hh_parser.load_vacancies_from_json()
    ids = hh_parser.get_vacancy_ids()
    # ids = {'80199729', }
    for vacancy_id in ids:
        if vacancy_id not in hh_parser.vacancy_ids:
            vacancy = Vacancy.create_vacancy_from_id(vacancy_id)
            hh_parser.add_vacancy(vacancy)
    hh_parser.save_vacancies_to_json()
