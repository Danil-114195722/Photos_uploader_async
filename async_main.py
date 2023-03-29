#!./venv/bin/python


import time
import re
import os

import asyncio
import aiohttp
import aiofiles

import soupsieve
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


# скачиваем фото по ссылке
async def uploader(session, link, query, num):
    user_agent = UserAgent()

    underscore_query = re.sub("\s", "_", query)
    path = f'./async_all_pictures/catalog_{underscore_query}_pictures'

    # делаем запрос на страницу с картинкой
    tries_count = 1
    while tries_count <= 3:
        try:
            async with session.get(link, headers={'User-Agent': user_agent.random}, timeout=2) as response_picture:
                # побитно читаем и загружаем картинку
                async with aiofiles.open(f'{path}/{underscore_query}_{num}.jpg', 'wb') as picture:
                    await picture.write(await response_picture.read())
                    print(f'File number {num} have uploaded!')
            break
        except asyncio.exceptions.TimeoutError:
            print(f'File number {num} corrupted :( I try again...')
            tries_count += 1
            await asyncio.sleep(1)


# главная сопрограмма
async def main(query, resolution=1200):
    user_agent = UserAgent()

    # путь к директории
    underscore_query = re.sub("\s", "_", query)
    path = f'./async_all_pictures/catalog_{underscore_query}_pictures'
    # начальная страница
    slug_query = re.sub("\s", "-", query)
    default_url = f'https://unsplash.com/s/photos/{slug_query}'

    # список задач
    tasks = []
    # список всех ссылок
    links = []

    # создаём асинхронную сессию
    async with aiohttp.ClientSession() as session:

        while True:
            try:
                # делаем запрос на основную страницу со всеми картинками по запросу
                async with session.get(default_url, headers={'User-Agent': user_agent.random}, timeout=2) as response:
                    html = await response.text()
                    # получаем все ссылки с разными разрешениями на все фото
                    soup = BeautifulSoup(html, 'lxml')
                    img_tegs = soupsieve.select('figure img', soup)

                    # если по запросу ничего не найдено
                    if not img_tegs:
                        print('Nothing found for your request :(')
                        return

                    # выбираем только ссылки с разрешением "resolution" (по умолчанию 1200x800)
                    for img in img_tegs:
                        one_srcset = img['srcset'].split(',')
                        for src in one_srcset:
                            if re.match(f'.*&w={resolution}&.*', src):
                                links.append(re.sub(f'{resolution}w$|\s', r'', src))
                    links = list(set(links))

                    # создаём директорию для фото
                    try:
                        os.mkdir(path)
                    # если такая директория существует, то чистим её (предварительно спросив у пользователя)
                    except OSError:
                        print('Do you agree that I can clear this directory? [y, n]', end=' ')
                        while True:
                            answer = input()
                            if answer in ['y', 'д']:
                                for file in os.listdir(path):
                                    os.remove(f'{path}/{file}')
                                break
                            elif answer in ['n', 'н']:
                                print("Videos haven't been downloaded")
                                raise Exception
                            else:
                                print('Wrong parameters have been entered! Try again [y, n]', end=' ')

                    # заполняем список задач задачами
                    for num, link in enumerate(links, 1):
                        task = asyncio.create_task(uploader(session, link, query, num))
                        tasks.append(task)
                    await asyncio.gather(*tasks)

                # если файлы скачивались
                try:
                    # удаляем пустые файлы
                    for file in os.listdir(path):
                        path_file = f'{path}/{file}'
                        # если размер файла - 0 байт
                        if os.stat(path_file).st_size == 0:
                            os.remove(path_file)

                    # печатает, сколько файлов было установлено
                    print(f'\n{str(len(os.listdir(path)))} files have been uploaded')
                    # и сколько прошло секунд с начала программы
                    print(f'{str(round(start - time.time(), 2))} seconds have passed')
                # если по запросу ничего не найдено, то ничего не делаем
                except FileNotFoundError:
                    pass
                break
            except asyncio.exceptions.TimeoutError:
                print("I'm sorry, wait some time, please :( I try again...")
                time.sleep(1)
            except Exception:
                print("I'm sorry, we have some server problems :(")
                break


if __name__ == '__main__':
    # запрос пользователя
    query = input('What pictures do you wanna upload?\n')
    # путь к папке с фото (также указывается разрешение, если оно есть, но запрос производится без указания разрешения)
    underscore_query = re.sub("\s", "_", query)
    path = f'./async_all_pictures/catalog_{underscore_query}_pictures'

    # время начала работы программы
    start = time.time()
    # проверка на объявление разрешения и запуск очереди сопрограмм
    try:
        potentially_resolution = query.split(' ')[-1]
        # разрешение указывается после запроса в таком формате: "res{само разрешение, т.е. число}"
        if re.match('res\d{1,2}00', potentially_resolution):
            resolution = re.sub('res', '', potentially_resolution)
            # убираем из запроса разрешение для более корректного поиска, но оставляем его в названии директории
            query = ''.join(query.split(' ')[:-1])
            # вызов очереди задач
            asyncio.run(main(query, resolution))
        # если последнее слово запроса не соответствует схеме разрешения
        else:
            raise ValueError
    except ValueError:
        # вызов очереди задач
        asyncio.run(main(query))
