import os
from pathlib import Path
from django.conf import settings
from django.template.loader import render_to_string
from weasyprint import CSS, HTML
from weasyprint.text.fonts import FontConfiguration
from main.models import Settings
CSS_PATH = Path('static/assets/css/diplom.css')

class Cfg:

    def __call__(self, name):
        try:
            cfg = Settings.objects.get(name=name)
        except Settings.DoesNotExist:
            cfg = Settings(name=name, value='')
            cfg.save()

        return cfg.value

Configuration = Cfg()

def generate_diploma(participants, team, coach):
    try:
        output_pdf = f'diploma{team}.pdf'
        html_content = render_to_string(settings.TEMPLATE_PATH, context={
            'participants': participants,
            'team': team,
            'coach': coach,
        })

        with open(CSS_PATH, 'r', encoding='utf-8') as css_file:
            css_content = css_file.read()
        css_content = css_content.replace('./Diploma_1.png', Configuration("diploma.image.url"))
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
