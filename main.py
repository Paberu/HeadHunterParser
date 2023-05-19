from pprint import pprint

from HHParser import HHParser
from Vacancy import Vacancy

if __name__ == '__main__':
    search = input('Введите через пробел слова, по которым пойдёт поиск вакансий:').split()
    if len(search) > 1:
        search = '+'.join(search)
    elif len(search) == 1:
        search = search[0]
    else:
        print('Вы забыли ввести поисковые слова.')
        exit(1)

    remote = input('Вы ищете работу по удалёнке? Д/н')
    if remote not in ('Н', 'н', 'Y', 'y'):
        schedule = 'remote'
    else:
        schedule = ''

    hh_parser = HHParser(search, schedule)
    hh_parser.load_vacancies_from_json()
    ids = hh_parser.get_first_50_vacancie_ids()
    # ids = {'79582780', }
    for vacancy_id in ids:
        if vacancy_id not in hh_parser.vacancy_ids:
            vacancy = Vacancy.create_vacancy_from_id(vacancy_id)
            hh_parser.add_vacancy(vacancy)
    # hh_parser.save_vacancies_to_json()
    for vacancy in hh_parser.vacancies:
        print(vacancy.parse_salary(vacancy.salary))
    pprint(hh_parser.split_vacancies_by_salary())
