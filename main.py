#!./venv/bin/python


import re
import os
from time import time

import requests
import soupsieve
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


def download_pictures(query, resolution=1200) -> None:
    global user_agent

    # строка для ввода в поисковике
    slug_query = re.sub("\s", "-", query)
    # строка для названия папки
    underscore_query = re.sub("\s", "_", query)


    default_url = f'https://unsplash.com/s/photos/{slug_query}'
    path = f'./all_pictures/catalog_{underscore_query}_pictures'

    # делаем запрос на основную страницу со всеми картинками по запросу
    try:
        res = requests.get(default_url, headers={'User-Agent': user_agent.random}, timeout=5)
        html = res.text
    except Exception as error:
        print('You got error:', error)
        return

    # получаем все ссылки с разными разрешениями на все фото
    soup = BeautifulSoup(html, 'lxml')
    img_tegs = soupsieve.select('figure img', soup)

    # если по запросу ничего не найдено
    if not img_tegs:
        print('Nothing found for your request :(')
        return

    # выбираем только ссылки с разрешением "resolution" (по умолчанию 1200x800)
    links = []
    for img in img_tegs:
        one_srcset = img['srcset'].split(',')
        for src in one_srcset:
            if re.match(f'.*&w={resolution}&.*', src):
                links.append(re.sub(f'{resolution}w$|\s', r'', src))
    links = list(set(links))

    # создаём каталог для фото
    try:
        os.mkdir(path)
    # если такой каталог существует, то удаляем его содержимое
    except OSError:
        for file in os.listdir(path):
            os.remove(f'{path}/{file}')

    # скачиваем фото с разрешением "resolution" (по умолчанию 1200x800) по всем полученным ссылкам
    for num, link in enumerate(links, 1):
        # делаем запрос на страницу с картинкой
        try:
            res_from_picture = requests.get(link, headers={'User-Agent': user_agent.random}, timeout=5, stream=True)
        except Exception:
            break

        # побитно читаем и загружаем картинку
        with open(f'{path}/{underscore_query}_{num}.jpg', 'wb') as picture:
            for chunk in res_from_picture.iter_content(1024 * 20):
                picture.write(chunk)
                print('.', end='')
        print('Done!')
    else:
        # если скачались все фото (и не возникло ошибки)
        print('\nAll Right!')

    print(f'\n{str(len(os.listdir(path)))} files have been uploaded')


if __name__ == '__main__':
    user_agent = UserAgent()

    query = list(input('What pictures do you wanna upload?\n').split(' '))

    start = time()
    if len(query) == 1:
        download_pictures(query[0])
    elif len(query) == 2:
        download_pictures(query[0], query[1])
    else:
        print('You have entered bad parameters!')

    print(f'{str(round(start - time(), 2))} seconds have passed')
