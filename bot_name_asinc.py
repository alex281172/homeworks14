import pprint
import telebot
from telebot import types
import requests
from telebot.async_telebot import AsyncTeleBot
import asyncio

TOKEN = '5247529999:AAEwdEr1aEx4RcKDyLapU8jet-vk-qqulVo'

bot = AsyncTeleBot(TOKEN)


@bot.message_handler(commands=['start'])
async def send_welcome(message):
    pprint.pprint(message.json)
    first_name = message.chat.first_name
    last_name = message.chat.last_name
    await bot.send_message(message.chat.id, f'Привет, {first_name} {last_name}!')


@bot.message_handler(commands=['help'])
async def send_welcome(message):
    await bot.send_message(message.chat.id, f'Это бот-парсер основных навыков выбранной профессии с hh.ru и распределение по городам')
    await bot.send_message(message.chat.id, f'Парсер запускается командой /pars')


@bot.message_handler(commands=['pars'])

async def parsing(message):
    await bot.send_message(message.chat.id, f'Укажите профессию:')
    @bot.message_handler(content_types=['text'])
    async def profession(message):
        proff = message.text
        print(proff)


        import requests
        import pprint
        from collections import Counter
        from operator import itemgetter
        import json

        DOMAIN = 'https://api.hh.ru/'
        url_vacancies = f'{DOMAIN}vacancies'

        # def hhparser(proff = 'Python developer'):
        my_skill_list = []
        my_city_list = []
        total_skill = []
        total_city = []
        main_count = 0

        modify_my_city_list = []
        modify_skill_list = []

        page = 1

        # Перебор страниц

        await bot.send_message(message.chat.id, f'Парсинг вакансии {proff}')

        for page_count in range(page):

            await bot.send_message(message.chat.id, f'Парсинг страницы {page_count + 1}')
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
                    await bot.send_message(message.chat.id, f'Анализ {main_count} осталось: {page * 20 - main_count}')
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

        print(f'Всего {total_result} вакансий найдено')
        await bot.send_message(message.chat.id, f'Всего {total_result} вакансий найдено')
        print(f'{main_count} вакансий {proff} спарсено')
        await bot.send_message(message.chat.id, f'{main_count} вакансий {proff} спарсено')



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


        f = open('city.json', 'w')
        f.write(result_city_json)
        f.close()
        print('Успешно создан файл city.fson со списком городов')



        await bot.send_message(message.chat.id, f'Успешно создан файл result.json со списком необходимых навыков.')

        with open('result.json', 'rb') as new_file:
            await bot.send_document(message.chat.id, new_file)

        await bot.send_message(message.chat.id, f'Успешно создан файл city.json со списком городов.')

        with open('city.json', 'rb') as new_file:
            await bot.send_document(message.chat.id, new_file)




asyncio.run(bot.polling())


#Командя для telegram

# start - greeting
# help - help
# pars - parsing hh.ru



