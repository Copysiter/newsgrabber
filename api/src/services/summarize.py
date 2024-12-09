import openai
import httpx
from fastapi import HTTPException
from core.config import settings


async def openai_summarize(source_name: str, title: str, text: str) -> str:
    """
    Получить краткое содержание текста с использованием OpenAI API.

    :param text: Полный текст статьи.
    :param openai_api_key: Ключ API OpenAI.
    :param max_tokens: Максимальное количество токенов для ответа.
    :param temperature: Уровень "случайности" ответа модели .
    :param proxy_url: URL прокси-сервера.
    :return: Краткое содержание текста.
    """
    if not text.strip():
        raise HTTPException(
            status_code=400, detail='Текст статьи не может быть пустым.'
        )

    client = openai.AsyncOpenAI(
        api_key=settings.OPENAI_API_KEY,
        http_client=httpx.AsyncClient(
            verify=False,
            proxy=settings.OPENAI_PROXY_URL \
                if settings.OPENAI_PROXY_URL else None,
        )
    )

    prompt = f'''
            Сделай саммари текста публикации СМИ на русском языке.
            Суть саммари: передать читателю всё максимально важное из публикации в лапидарной форме, но не слишком короткой. Нужно, чтобы пост выглядел интересным для читателя, а не сухим и скучным. 
            Структура Саммари (в том же порядке): Название СМИ на английском языке, двоеточие, оригинальный заголовок статьи, переведённый на русский язык. Не используй выделение жирным. 
            Вторым абзацем саммари от 5 до 7 ключевых новостных посылов/идей/фактов/смыслов из публикации. 
            В саммари обязательно обращай внимание не только на смыслы, но и наиболее важные и свежие данные, цифры и показатели. 
            Сохраняй в тексте саммари тональность и посылы оригинальной статьи, чтобы читатель саммари понимал тональность, которая использована в оригинальной статье. 
            Бери из оригинального текста важный исторический контекст. В пунктах саммари пиши суть, не формулируй очевидные идеи, которые не являются полезными для читателя. 
            Используй одну самую лучшую, яркую, интересную цитату и подписывай автора вместе с его именем и должностью. 
            Саммари должно быть оформлено в виде готового поста для канала в Telegram, но не должно быть куцым. Используй тематические эмоджи рядом с каждым тезисом/буллетом (например, если буллет о нефти, ставь эмоджи с баррелью нефти). 
            Название СМИ: {source_name}
            Оригинальный заголовок: {title}
            Текст статьи: {text}
            '''
    context = 'Ты профессиональный журналист, создающий лаконичные саммари новостей.'

    try:
        # Отправить запрос к OpenAI API
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            max_tokens=settings.OPENAI_MAX_TOKENS,
            temperature=settings.OPENAI_TEMPERATURE,
            messages=[
                {'role': 'system', 'content': context},
                {'role': 'user', 'content': prompt}
            ],
        )
        # Извлечь и вернуть результат
        summary = response.choices[0].message.content.strip()
        return summary
    except openai.AuthenticationError as e:
        raise HTTPException(
            status_code=401, detail=f'Ошибка аутентификации OpenAI API: {e}'
        )
    # except openai.APIError as e:
    #     raise HTTPException(
    #         status_code=502, detail=f'Ошибка API OpenAI: {e}'
    #     )
    # except openai.OpenAIError as e:
    #     raise HTTPException(
    #         status_code=500, detail=f'Ошибка при вызове OpenAI API: {e}'
    #     )
    # except Exception as e:
    #     raise HTTPException(
    #         status_code=500, detail=f'Неизвестная ошибка: {e}'
    #     )
