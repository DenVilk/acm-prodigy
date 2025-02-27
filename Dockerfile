FROM python:3.12-alpine

WORKDIR /app

EXPOSE 8000

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]