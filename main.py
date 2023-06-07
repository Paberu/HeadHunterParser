from pprint import pprint

import dearpygui.dearpygui as dpg

from HHParser import HHParser
from Vacancy import Vacancy


# задать ключевой параметр - константу или переменную размер шрифта, можно вычислять автоматически по
# разрешению экрана. Высоты всех виджетов в пикселях высчитывать исходя из размера шрифта.
if __name__ == '__main__':

    FONT_SIZE = 14
    SEARCH_WIDGET_HEIGHT = (FONT_SIZE + 1) * 10 + 10
    FILTER_WIDGET_HEIGHT = (FONT_SIZE + 1) * 25 + 10
    VACANCIES_WIDGET_HEIGHT = SEARCH_WIDGET_HEIGHT + FILTER_WIDGET_HEIGHT
    SMALL_WIDGET_HEIGHT = (FONT_SIZE + 1) * 4
    WIDGET_WIDTH = 500

    main_data = {
        'hh_parser': None,
        'vacancies': [],
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
        main_data['vacancies'] = hh_parser.vacancies
        main_data['key_skills'] = hh_parser.sort_key_skills()
        main_data['salaries'] = hh_parser.split_vacancies_by_salary()
        main_data['experience'] = hh_parser.experience
        dpg.configure_item(vacancies_list, items=list(main_data['vacancies']))
        dpg.configure_item('salary_label', show=True)
        dpg.configure_item(salaries_list, items=list(main_data['salaries']), show=True)
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
        filtered_vacancies_experience = {'не требуется': 0, '1–3 года': 0, '3–6 лет': 0, 'более 6 лет': 0}
        for vacancy in main_data['hh_parser'].vacancies:
            if salary_position != 0:
                for salary_part in vacancy.salary:
                    if lowest_salary < salary_part < highest_salary:
                        if vacancy not in filtered_vacancies:
                            filtered_vacancies.append(vacancy)
                            filtered_vacancies_experience[vacancy.experience] += 1
                            continue
            else:
                if not vacancy.salary:
                    if vacancy not in filtered_vacancies:
                        filtered_vacancies.append(vacancy)
                        filtered_vacancies_experience[vacancy.experience] += 1

        main_data['filtered_vacancies'] = filtered_vacancies
        dpg.configure_item(vacancies_list, items=filtered_vacancies, show=True)
        dpg.configure_item(experience_list, items=list(filtered_vacancies_experience), show=True)
        dpg.configure_item('experience_label', show=True)

    def filter_by_experience(sender, data):
        filtered_vacancies = []
        for vacancy in main_data['filtered_vacancies']:
            if vacancy.experience == data:
                filtered_vacancies.append(vacancy)
        dpg.configure_item(vacancies_list, items=filtered_vacancies)

    def filter_by_key_skills(sender, data):
        filtered_vacancies = []
        key_skill = data.split('-')[0].strip()
        for vacancy in main_data['hh_parser'].vacancies:
            if key_skill in vacancy.key_skills:
                filtered_vacancies.append(vacancy)
        dpg.configure_item(vacancies_list, items=filtered_vacancies)

    dpg.create_context()

    with dpg.font_registry():
        with dpg.font(r'C:\Windows\Fonts\Arial.ttf', FONT_SIZE, default_font=True, id='default_font'):
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
    dpg.bind_font('default_font')

    with dpg.window(label='Настройка поиска', height=SEARCH_WIDGET_HEIGHT, width=WIDGET_WIDTH):
        dpg.add_text('Введите слова, по которым будет вестись поиск:')
        search = dpg.add_input_text(default_value='Python', width=WIDGET_WIDTH)
        remote = dpg.add_checkbox(label='Только удаленная работа?', default_value=True)
        dpg.add_text('Введите границы интересующего диапазона зарплат:')
        dpg.add_button(label='Начать поиск', callback=create_hhparser, user_data=[search, remote])

    with dpg.window(label='Фильтр вакансий', height=FILTER_WIDGET_HEIGHT, width=WIDGET_WIDTH,
                    pos=[0, SEARCH_WIDGET_HEIGHT]):
        dpg.add_text('Выберите диапазон зарплат:', show=False, tag='salary_label')
        salaries_list = dpg.add_listbox(items=list(main_data['salaries']),
                                        num_items=10, width=WIDGET_WIDTH,
                                        callback=filter_by_salary,
                                        show=False)
        dpg.add_text('Выберите желаемый опыт работы:', show=False, tag='experience_label')
        experience_list = dpg.add_listbox(items=list(main_data['experience'].values()),
                                          num_items=5, width=WIDGET_WIDTH,
                                          callback=filter_by_experience,
                                          show=False)
        dpg.add_text('Выберите ключевой навык из описания вакансии:', show=False, tag='key_skills_label')
        key_skills_list = dpg.add_listbox(items=list(main_data['key_skills']),
                                          num_items=10, width=WIDGET_WIDTH,
                                          callback=filter_by_key_skills,
                                          show=False)

    with dpg.window(label='Вакансии', height=VACANCIES_WIDGET_HEIGHT, width=WIDGET_WIDTH, pos=[WIDGET_WIDTH, 0]):
        vacancies_list = dpg.add_listbox(items=list(main_data['vacancies']),
                                         num_items=25, width=WIDGET_WIDTH,
                                         show=False)

    dpg.create_viewport(title='HHParser')
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()
