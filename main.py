from pprint import pprint
import dearpygui.dearpygui as dpg

from HHParser import HHParser
from Vacancy import Vacancy

if __name__ == '__main__':

    main_data = {
        'hh_parser': None,
        'vacancies': {},
        'key_skills': {},
        'salaries': {},
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
        hh_parser.get_vacancies()
        main_data['hh_parser'] = hh_parser
        for vacancy in hh_parser.vacancies:
            main_data['vacancies'][vacancy.id] = vacancy.title
        main_data['key_skills'] = hh_parser.key_skills
        dpg.configure_item(vacancies_list, items=list(main_data['vacancies'].values()))
        dpg.configure_item(salaries_list, items=list(main_data['salaries'].values()))
        dpg.configure_item(key_skills_list, items=list(main_data['key_skills'].values()))
        dpg.configure_item(experience_list, items=list(main_data['experience'].values()))

    dpg.create_context()
    with dpg.font_registry():
        with dpg.font(r'C:\Windows\Fonts\Arial.ttf', 14, default_font=True, id='default_font'):
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
    dpg.bind_font('default_font')

    with dpg.window(label='Настройка поиска', height=130, width=500):
        dpg.add_text('Введите, что будем искать:')
        search = dpg.add_input_text(label='Введите слова, по которым будет вестись поиск.', default_value='Python',
                                    width=150)
        remote = dpg.add_checkbox(label='Только удаленная работа?', default_value=True)
        dpg.add_button(label='Начать поиск', callback=create_hhparser, user_data=[search, remote])

    with dpg.window(label='Вакансии', height=300, width=500, pos=[0, 130]):
        vacancies_list = dpg.add_listbox(items=list(main_data['vacancies'].values()))

    with dpg.window(label='Выберите диапазон зарплат.', height=300, width=500, pos=[500, 0]):
        salaries_list = dpg.add_listbox(items=list(main_data['salaries'].values()))

    with dpg.window(label='Выбрать ключевые навыки.', height=300, width=500, pos=[500, 300]):
        key_skills_list = dpg.add_listbox(items=list(main_data['key_skills'].values()))

    with dpg.window(label='Выбрать стаж.', height=300, width=500, pos=[500, 600]):
        experience_list = dpg.add_listbox(items=list(main_data['experience'].values()))

    dpg.create_viewport(title='HHParser', width=505, min_height=1030, max_height=800)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()
