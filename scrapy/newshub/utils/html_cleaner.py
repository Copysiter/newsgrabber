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
