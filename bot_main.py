import telebot
import requests
import pprint
from collections import Counter
from operator import itemgetter
import json
from telebot import types

TOKEN = '5247529999:AAEwdEr1aEx4RcKDyLapU8jet-vk-qqulVo'

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    pprint.pprint(message.json)
    first_name = message.chat.first_name
    last_name = message.chat.last_name
    bot.send_message(message.chat.id, f'Привет, {first_name} {last_name}!')


@bot.message_handler(commands=['help'])
def send_welcome(message):
    pprint.pprint(message.json)
    bot.send_message(message.chat.id, f'Это бот-парсер основных навыков выбранной профессии с hh.ru и распределение по городам')
    bot.send_message(message.chat.id, f'Парсер запускается командой /pars')

# Команда в параметром
@bot.message_handler(commands=['pars'])
def size(message):
    msg = bot.send_message(message.chat.id, f'Укажите количество страниц для парсинга (не более 10):')
    bot.register_next_step_handler(msg, parsing)


def parsing(message):

    size = message.text
    if not size.isdigit() or int(size) > 10 or int(size) <= 0:
        msg = bot.reply_to(message, 'укажите правильно количество страниц для парсинга (не более 10):')
        bot.register_next_step_handler(msg, parsing)
        return


    bot.send_message(message.chat.id, f'Укажите профессию:')

    @bot.message_handler(content_types=['text'])
    def profession(message):

        proff = message.text
        print(proff)


        DOMAIN = 'https://api.hh.ru/'
        url_vacancies = f'{DOMAIN}vacancies'

        # def hhparser(proff = 'Python developer'):
        my_skill_list = []
        my_city_list = []
        total_skill = []
        total_city = []
        main_count = 0
        total_result = 0


        page = int(size)

        # Перебор страниц

        bot.send_message(message.chat.id, f'Парсинг вакансии {proff}')

        for page_count in range(page):

            bot.send_message(message.chat.id, f'Парсинг страницы {page_count + 1}')
            print(f'Парсинг страницы {page_count + 1}')
            params = {
                'text': proff,
                'page': page_count
            }
            page_count += 1
            vacancy_count = 0
            # Перебор 20 вакансий на странице
            for k in range(20):
                try:
                    main_count += 1
                    vacancy_count += 1
                    # Сколько ваканский спарсили на текущей странице
                    print(f'Анализ {main_count} осталось: {page * 20 - main_count}')
                    bot.send_message(message.chat.id, f'Анализ {main_count} осталось: {page * 20 - main_count}')
                    # Вытаскиваем нужный url (где есть skill) для дальнейшей обработки
                    result = requests.get(url_vacancies, params=params).json()
                    url_skill = result['items'][k]['url']
                    my_result = requests.get(url_skill).json()
                    # Записываем Skill в список
                    my_skill = my_result['key_skills']
                    lens = len(my_skill)

                    if len(my_skill) != 0:
                        for counter in range(lens):
                            my_skill_list.append(my_skill[counter]['name'])
                    else:
                        pass

                    my_name = my_result['name']
                    my_address = my_result['area']
                    if my_address == None:
                        my_city = 'Неизвестно'

                    else:
                        my_city = my_address['name']

                    my_city_list.append(my_city)
                except:
                    pass

            total_result = result['found']




        print(f'{main_count} вакансий {proff} спарсено')
        bot.send_message(message.chat.id, f'{main_count} вакансий {proff} спарсено')

        print(f'Всего {total_result} вакансий найдено')
        bot.send_message(message.chat.id, f'Всего {total_result} вакансий найдено')

        lens_skill_list = len(my_skill_list)
        lens_my_city_list = len(my_city_list)

        modify_skill_list = Counter(my_skill_list)
        modify_my_city_list = Counter(my_city_list)

        lens_end_skill = len(modify_skill_list)
        lens_end_city = len(modify_my_city_list)

        for counter in range(lens_end_skill):
            name = list(modify_skill_list.keys())[counter]
            count = list(modify_skill_list.values())[counter]
            path = count / lens_skill_list
            percent = '{percent:.1%}'.format(percent=path)

            total_skill.append({'name': name, 'percent': percent, 'count': count})

        total_skill = (sorted(total_skill, key=itemgetter('count'), reverse=True))

        result_skill = {
            'keywords': proff,
            'count': str(lens_end_skill),
            'requirements': total_skill
        }
        result_skill_json = json.dumps(result_skill, ensure_ascii=False, indent=4)

        for counter in range(lens_end_city):
            name = list(modify_my_city_list.keys())[counter]
            count = list(modify_my_city_list.values())[counter]
            path = count / lens_my_city_list
            percent = '{percent:.1%}'.format(percent=path)

            total_city.append({'name': name, 'percent': percent, 'count': count})

        total_city = (sorted(total_city, key=itemgetter('count'), reverse=True))

        result_city = {
            'keywords': proff,
            'dispersion': total_city
        }

        result_city_json = json.dumps(result_city, ensure_ascii=False, indent=4)

        f = open('result.json', 'w')
        f.write(result_skill_json)
        f.close()
        print('Успешно создан файл result.fson со списком необходимых навыков')
        bot.send_message(message.chat.id, f'Успешно создан файл result.json со списком необходимых навыков')

        f = open('city.json', 'w')
        f.write(result_city_json)
        f.close()

        print('Успешно создан файл city.fson со списком городов')
        bot.send_message(message.chat.id, f'Успешно создан файл city.json со списком городов')

        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('ДА', 'НЕТ')
        msg = bot.send_message(message.chat.id, 'Вам нужны файлы отчетов?', reply_markup=markup)
        bot.register_next_step_handler(msg, file_send_step)


    def file_send_step(message):
        first_name = message.chat.first_name
        last_name = message.chat.last_name
        try:
            if message.text == u'ДА':
                with open('result.json', 'rb') as data:
                    bot.send_document(message.chat.id, data)
                with open('city.json', 'rb') as data:
                    bot.send_document(message.chat.id, data)
                bot.send_message(message.chat.id, f'Спасибо за использование бота, {first_name} {last_name}!')
            elif message.text == u'НЕТ':
                bot.send_message(message.chat.id, f'Всего хорошего, {first_name} {last_name}!' )
            else:
                raise Exception('Ошибка выбора')
        except:
            bot.send_message(message.chat.id, 'Неизвестная команда')



bot.infinity_polling()


#Команды для telegram

# start - greeting
# help - help
# pars - parsing hh.ru