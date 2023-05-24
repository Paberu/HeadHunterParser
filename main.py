from pprint import pprint
import dearpygui.dearpygui as dpg

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
    hh_parser.get_vacancies()
    hh_parser.save_vacancies_to_json()

    pprint(hh_parser.experience)
