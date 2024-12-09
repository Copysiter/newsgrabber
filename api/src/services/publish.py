from telegraph import Telegraph
from core.config import settings


def publish_to_telegraph(title, html, source_url):
    telegraph = Telegraph(settings.TELEGRAPH_TOKEN)
    html = f'{html}<p>Источник: <a href="{source_url}">{source_url}</a></p>'
    response = telegraph.create_page(
        title=title, html_content=html,
    )
    return 'https://telegra.ph/' + response['path']