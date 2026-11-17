FROM python:3.12-alpine

ENV APP_HOME=/app

WORKDIR $APP_HOME

RUN mkdir -p $APP_HOME/staticfiles
RUN mkdir -p $APP_HOME/media

COPY pyproject.toml poetry.lock $APP_HOME/

RUN apk add --no-cache \
    build-base \
    libffi-dev \
    cairo-dev \
    pango-dev \
    gdk-pixbuf-dev \
    musl-dev \
    py3-pip \
    python3-dev \
    gcc \
    jpeg-dev \
    zlib-dev \
    libxml2-dev \
    libxslt-dev \
    ttf-freefont

RUN apk add weasyprint
RUN apk add ghostscript

RUN python -m pip install --no-cache-dir poetry==1.7.1 \
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi \
    && rm -rf $(poetry config cache-dir)/{cache,artifacts}

COPY entrypoint.sh $APP_HOME/
COPY . $APP_HOME

RUN chmod +x $APP_HOME/entrypoint.sh

ENTRYPOINT ["sh", "/app/entrypoint.sh"]