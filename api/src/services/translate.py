import time
import logging
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator

from core.config import settings


def split_text(text, max_length=5000):
    """
    Разбивает текст на части длиной менее max_length символов.
    """
    chunks = []
    while len(text) > max_length:
        split_index = text[:max_length].rfind('. ')
        if split_index == -1:  # Если пробел не найден, принудительно обрезаем
            split_index = max_length
        chunks.append(text[:split_index+1])
        text = text[split_index-1:].lstrip()
    chunks.append(text)
    return chunks

def google_translate(text: str, source: str = 'auto', target: str = 'ru'):
    """
    Переводит длинный текст, разбивая его на части, если это необходимо.
    """
    start = time.time()
    def translate_element(text: str, source: str = 'auto', target: str = 'ru'):
        chunks = split_text(text)
        translated_chunks = []
        translator = GoogleTranslator(source=source, target=target, proxies={
            'all': settings.TRANSLATE_PROXY_URL
        } if settings.TRANSLATE_PROXY_URL else None)
        for chunk in chunks:
            translated_chunk = translator.translate(chunk) or chunk
            translated_chunks.append(translated_chunk)
        return ' '.join(translated_chunks)

    html = BeautifulSoup(text, 'html.parser')

    for element in html.find_all(string=True):
        if element.parent.name not in ['script', 'style']:
            original_text = str(element)
            translated_text = translate_element(original_text)
            element.replace_with(translated_text)

    logging.info(f'{time.time() - start} sec.')

    return str(html)