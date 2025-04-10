import os
from django.conf import settings
from django.template.loader import render_to_string
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

TEMPLATE_PATH = os.path.join('diplom', 'diplom.html')
CSS_PATH = os.path.join('static', 'assets', 'css', 'diplom.css')
BACKGROUND_IMAGE_PATH = os.path.join(settings.BASE_DIR, 'static', 'assets', 'img', 'Diploma_1.png')
ABSOLUTE_IMAGE_PATH = f'file://{BACKGROUND_IMAGE_PATH.replace(os.sep, "/")}'
def generate_diploma(participants, team, coach):
    try:
        output_pdf = f'diploma{team}.pdf'
        html_content = render_to_string(TEMPLATE_PATH, context={
            'participants': participants,
            'team': team,
            'coach': coach,
        })

        with open(CSS_PATH, 'r', encoding='utf-8') as css_file:
            css_content = css_file.read()
        css_content = css_content.replace('./Diploma_1.png', ABSOLUTE_IMAGE_PATH)
        font_config = FontConfiguration()
        html = HTML(string=html_content)
        css = CSS(string=css_content, font_config=font_config)

        html.write_pdf(
            output_pdf,
            stylesheets=[css],
            font_config=font_config
        )

        print(f"Диплом успешно сохранён в {output_pdf}")

    except Exception as e:
        print(f"Ошибка генерации: {str(e)}")
