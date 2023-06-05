from pprint import pprint

import dearpygui.dearpygui as dpg

from HHParser import HHParser
from Vacancy import Vacancy


# задать ключевой параметр - константу или переменную размер шрифта, можно вычислять автоматически по
# разрешению экрана. Высоты всех виджетов в пикселях высчитывать исходя из размера шрифта.
if __name__ == '__main__':

    FONT_SIZE = 14
    WIDGET_HEIGHT = (FONT_SIZE + 1) * 10
    SMALL_WIDGET_HEIGHT = (FONT_SIZE + 1) * 4
    WIDGET_WIDTH = 500

    main_data = {
        'hh_parser': None,
        'vacancies': {},
        'key_skills': {},
        'salaries': [],
        'experience': {}
    }

    def create_hhparser(sender, data, user_data):
        search = dpg.get_value(user_data[0]).split()
        if len(search) > 1:
            search = '+'.join(search)
        elif len(search) == 1:
            search = search[0]

        if dpg.get_value(user_data[1]):
            schedule = 'remote'
        else:
            schedule = ''

        hh_parser = HHParser(search, schedule)
        hh_parser.load_vacancies_from_json()
        # hh_parser.get_vacancies()
        # hh_parser.save_vacancies_to_json()

        main_data['hh_parser'] = hh_parser
        for vacancy in hh_parser.vacancies:
            main_data['vacancies'][vacancy.id] = vacancy.title
        main_data['key_skills'] = hh_parser.sort_key_skills()
        main_data['salaries'] = hh_parser.split_vacancies_by_salary()
        main_data['experience'] = hh_parser.experience
        dpg.configure_item(vacancies_list, items=list(main_data['vacancies'].values()))
        dpg.configure_item(salaries_list, items=list(main_data['salaries']))
        dpg.configure_item(key_skills_list, items=list(main_data['key_skills']))
        dpg.configure_item(experience_list, items=list(main_data['experience']))

    def filter_by_salary(sender, data):

        for position, value in enumerate(main_data['salaries']):
            if value == data:
                salary_position = position
                break

        if salary_position == 0:
            lowest_salary = highest_salary = 0
        elif salary_position == 11:
            lowest_salary = 400000
            highest_salary = float('infinity')
        else:
            highest_salary = salary_position * 40000
            lowest_salary = highest_salary - 40000

        filtered_vacancies = []
        for vacancy in main_data['hh_parser'].vacancies:
            if salary_position != 0:
                for salary_part in vacancy.salary:
                    if lowest_salary < salary_part < highest_salary:
                        filtered_vacancies.append(vacancy)
                        continue
            else:
                if not vacancy.salary:
                    filtered_vacancies.append(vacancy)

        dpg.configure_item(vacancies_list, items=filtered_vacancies)

    dpg.create_context()

    # # getting the window sizes
    # main_width = dpg.get_item_width("Main")
    # main_height = dpg.get_item_height("Main")
    # print(f'{main_width}x{main_height}')
    #
    with dpg.font_registry():
        with dpg.font(r'C:\Windows\Fonts\Arial.ttf', FONT_SIZE, default_font=True, id='default_font'):
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
    dpg.bind_font('default_font')

    with dpg.window(label='Настройка поиска', height=WIDGET_HEIGHT, width=WIDGET_WIDTH):
        dpg.add_text('Введите слова, по которым будет вестись поиск:')
        search = dpg.add_input_text(default_value='Python', width=WIDGET_WIDTH)
        remote = dpg.add_checkbox(label='Только удаленная работа?', default_value=True)
        dpg.add_text('Введите границы интересующего диапазона зарплат:')
        # bottom_of_salary_range = dpg.add_input_int()
        # top_of_the_salary_range = dpg.add_input_int()
        dpg.add_button(label='Начать поиск', callback=create_hhparser, user_data=[search, remote])

    with dpg.window(label='Вакансии', height=2*WIDGET_HEIGHT, width=WIDGET_WIDTH, pos=[WIDGET_WIDTH, 0]):
        vacancies_list = dpg.add_listbox(items=list(main_data['vacancies'].values()),
                                         num_items=10, width=WIDGET_WIDTH)

    with dpg.window(label='Выберите диапазон зарплат.', height=WIDGET_HEIGHT, width=WIDGET_WIDTH, pos=[0, WIDGET_HEIGHT]):
        salaries_list = dpg.add_listbox(items=list(main_data['salaries']),
                                        num_items=10, width=WIDGET_WIDTH,
                                        callback=filter_by_salary)

    with dpg.window(label='Выбрать ключевые навыки.', height=WIDGET_HEIGHT, width=WIDGET_WIDTH, pos=[0, WIDGET_HEIGHT*2]):
        key_skills_list = dpg.add_listbox(items=list(main_data['key_skills']), num_items=10, width=WIDGET_WIDTH)

    with dpg.window(label='Выбрать стаж.', height=SMALL_WIDGET_HEIGHT, width=WIDGET_WIDTH, pos=[0, WIDGET_HEIGHT*3]):
        experience_list = dpg.add_listbox(items=list(main_data['experience'].values()), num_items=4, width=WIDGET_WIDTH)

    dpg.create_viewport(title='HHParser', width=1005, min_height=800, max_height=1000)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()
