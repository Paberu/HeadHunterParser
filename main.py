import dearpygui.dearpygui as dpg

from HHParser import HHParser, translate_key_skills_dict_to_list


# задать ключевой параметр - константу или переменную размер шрифта, можно вычислять автоматически по
# разрешению экрана. Высоты всех виджетов в пикселях высчитывать исходя из размера шрифта.
if __name__ == '__main__':

    FONT_SIZE = 14
    SEARCH_WIDGET_HEIGHT = (FONT_SIZE + 1) * 10 + FONT_SIZE
    FILTER_WIDGET_HEIGHT = (FONT_SIZE + 1) * 45 + FONT_SIZE
    VACANCIES_WIDGET_HEIGHT = SEARCH_WIDGET_HEIGHT + FILTER_WIDGET_HEIGHT
    SMALL_WIDGET_HEIGHT = (FONT_SIZE + 1) * 4
    WIDGET_WIDTH = 500

    main_data = {
        'hh_parser': HHParser('', ''),
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
        # hh_parser.load_vacancies_from_json()
        hh_parser.get_vacancies()
        hh_parser.split_vacancies_by_salary()
        main_data['hh_parser'] = hh_parser
        dpg.configure_item('vacancies_list', items=list(hh_parser.vacancies))
        dpg.configure_item('salary_label', show=True)
        dpg.configure_item('salaries_list', items=list(hh_parser.salaries), show=True)

    def filter_by_salary(sender, data):
        hh_parser = main_data['hh_parser']
        for position, value in enumerate(hh_parser.salaries):
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

        hh_parser.filter_vacancies_by_salary(lowest_salary, highest_salary)

        dpg.configure_item('vacancy_window', show=True)
        dpg.configure_item('vacancies_list', items=hh_parser.vacancies_filtered_by_salaries, show=True)
        dpg.configure_item('experience_list', items=list(hh_parser.experience_filtered_by_salaries), show=True)
        dpg.configure_item('experience_label', show=True)

    def filter_by_experience(sender, data):
        filtered_vacancies = []
        key_skills = {}
        for vacancy in main_data['hh_parser'].vacancies_filtered_by_salaries:
            if vacancy.experience == data:
                filtered_vacancies.append(vacancy)
                for key_skill in vacancy.key_skills:
                    if key_skill not in key_skills.keys():
                        key_skills[key_skill] = 1
                    else:
                        key_skills[key_skill] += 1
        main_data['hh_parser'].vacancies_filtered_by_experience_and_salaries = filtered_vacancies
        main_data['hh_parser'].key_skills_filtered_by_experience_and_salaries = key_skills
        dpg.configure_item('vacancies_list', items=filtered_vacancies)
        dpg.configure_item('key_skills_label', show=True)
        dpg.configure_item('key_skills_list', items=translate_key_skills_dict_to_list(key_skills), show=True)

    def filter_by_key_skills(sender, data):
        hh_parser = main_data['hh_parser']
        if hh_parser.vacancies_filtered_by_experience_and_salaries:
            vacancies = hh_parser.vacancies_filtered_by_experience_and_salaries
        elif hh_parser.vacancies_filtered_by_salaries:
            vacancies = hh_parser.vacancies_filtered_by_salaries
        else:
            vacancies = hh_parser.vacancies
        filtered_vacancies = []
        key_skill = data.split('-')[0].strip()
        for vacancy in vacancies:
            if key_skill in vacancy.key_skills:
                filtered_vacancies.append(vacancy)
        dpg.configure_item('vacancies_list', items=filtered_vacancies)

    def show_vacancy_details(sender, data):
        vacancy_id, vacancy_title = data.split(maxsplit=1)
        hh_parser = main_data['hh_parser']
        if hh_parser.vacancies_filtered_by_experience_and_salaries:
            filtered_vacancies = hh_parser.vacancies_filtered_by_experience_and_salaries
        elif hh_parser.vacancies_filtered_by_salaries:
            filtered_vacancies = hh_parser.vacancies_filtered_by_salaries
        else:
            filtered_vacancies = hh_parser.vacancies

        for vacancy in filtered_vacancies:
            if vacancy.id == vacancy_id:
                dpg.configure_item('vacancy_details_window', show=True)
                dpg.configure_item('vacancy_id', default_value=vacancy_id)
                dpg.configure_item('vacancy_title', default_value=vacancy_title)
                dpg.configure_item('vacancy_body', default_value=vacancy.unparsed_information)

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
        dpg.add_listbox(items=list(main_data['salaries']), num_items=12, width=WIDGET_WIDTH, callback=filter_by_salary,
                        tag='salaries_list', show=False)
        dpg.add_text('Выберите желаемый опыт работы:', show=False, tag='experience_label')
        dpg.add_listbox(items=list(main_data['experience'].values()), num_items=4, width=WIDGET_WIDTH,
                        callback=filter_by_experience, tag='experience_list', show=False)
        dpg.add_text('Выберите ключевой навык из описания вакансии:', show=False, tag='key_skills_label')
        dpg.add_listbox(items=list(main_data['key_skills']), num_items=14, width=WIDGET_WIDTH,
                        callback=filter_by_key_skills, tag='key_skills_list', show=False)

    with dpg.window(label='Вакансии', height=VACANCIES_WIDGET_HEIGHT, width=WIDGET_WIDTH,
                    pos=[WIDGET_WIDTH, 0], tag='vacancy_window', show=False):
        dpg.add_listbox(items=list(main_data['vacancies']), num_items=44, width=WIDGET_WIDTH,
                        callback=show_vacancy_details, tag='vacancies_list', show=False)

    with dpg.window(label='Описание вакансии', height=VACANCIES_WIDGET_HEIGHT, width=WIDGET_WIDTH,
                    pos=[2*WIDGET_WIDTH, 0], tag='vacancy_details_window', show=False):
        dpg.add_text('##', tag='vacancy_id')
        dpg.add_text('Заголовок', tag='vacancy_title')
        dpg.add_text('Тело заявки', tag='vacancy_body')

    dpg.create_viewport(title='HHParser')
    dpg.setup_dearpygui()
    dpg.toggle_viewport_fullscreen()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()
