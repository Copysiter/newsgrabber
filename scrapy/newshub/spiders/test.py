'''
import requests
import json


response = requests.get(
    "https://www.thenationalnews.com/business/economy/2024/09/13/"
    "malaysia-on-track-to-sign-trade-treaty-with-uae-by-end-of-year/"
)

print(response.text)

'''

from bs4 import BeautifulSoup


def clean_html(html_content, allowed_tags=None, tag_replacements=None):
    # Создаем объект BeautifulSoup для разбора HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # Если список разрешенных тегов не передан, делаем его пустым
    if allowed_tags is None:
        allowed_tags = []

    # Если словарь для замены тегов не передан, делаем его пустым
    if tag_replacements is None:
        tag_replacements = {}

    # Проходим по всем тегам в HTML
    for tag in soup.find_all(True):  # True означает, что мы ищем все теги
        if tag.name in tag_replacements:
            # Меняем теги, которые указаны в словаре tag_replacements
            tag.name = tag_replacements[tag.name]
        elif tag.name not in allowed_tags:
            # Если тег не в списке разрешенных, удаляем его, но оставляем содержимое
            tag.unwrap()

    # Возвращаем очищенный текст
    return str(soup)


# Пример использования
html_content = '''
    <div><h1>Title</h1><p>Some <b>bold</b> text and <i>italic</i> text.</p><a href="#">Link</a></div>
'''
allowed_tags = ['b', 'i']  # Теги, которые нужно оставить
tag_replacements = {'h1': 'h2', 'a': 'span'}  # Замена тегов

cleaned_html = clean_html(html_content, allowed_tags, tag_replacements)
print(cleaned_html)
