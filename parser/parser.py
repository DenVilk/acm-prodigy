# import asyncio
# import aiohttp
# import json
# from aiohttp import BasicAuth
# from database import create_database, save_solution_to_db, check_solution_exists

# create_database()

# async def parse_accepted_solutions():
#     # Конфигурационные параметры
#     SOLVE_URL = "https://solve.bsuir.by/"
#     login = "denvilk"
#     password = "Prodigy@Netw0rk"
#     CONTEST_ID = 23  # ID соревнования
#     # Создаем сессию с общими настройками
#     async with aiohttp.ClientSession() as session:
#         try:
#             # 1. Аутентификация в системе
#             auth_url = f"{SOLVE_URL}/api/v0/login/"
#             async with session.post(auth_url, json={
#             'login': login,
#             'password': password
#         }
#         ) as auth_resp:
#                 if auth_resp.status != 201:
#                     error = await auth_resp.text()
#                     print(f"Ошибка авторизации: {auth_resp.status} - {error}")
#                     return
                
#                 print("Успешная авторизация в системе")
#                 cookies = auth_resp.cookies
            
#             # 2. Получаем поток событий
#             event_feed_url = f"{SOLVE_URL}api/ccs/contests/{CONTEST_ID}/event-feed"
#             async with session.get(event_feed_url, auth = BasicAuth(login, password)) as response:
#                 if response.status != 200:
#                     print(f"Ошибка получения event-feed: {response.status}")
#                     return
                
#                 print("Подключено к event-feed. Обработка данных...")
#                 buffer = ""
                
#                 async for chunk in response.content.iter_any():
#                     buffer += chunk.decode('utf-8')
                    
#                     # Обрабатываем построчно
#                     while "\n" in buffer:
#                         line, buffer = buffer.split("\n", 1)
#                         line = line.strip()
                        
#                         if not line:
#                             continue

#                         event = json.loads(line)
#                         if is_accepted_solution(event):
#                             await fetch_solution_details(session, cookies, SOLVE_URL, event)
        
#         except aiohttp.ClientError as e:
#             print(f"Сетевая ошибка: {e}")
#         except Exception as e:
#             print(f"Критическая ошибка: {e}")

# def is_accepted_solution(event):
#     """Проверяем, является ли событие Accepted решением"""
#     return (
#         event.get("type") == "judgements" and 
#         event.get("data", {}).get("judgement_type_id") == "AC"
#     )

# async def fetch_solution_details(session, cookies, base_url, event):
#     """Получаем детали решения"""
#     solution_id = event.get("data", {}).get("submission_id")
#     if not solution_id:
#         print("Отсутствует ID решения в событии")
#         return
    
#     solution_url = f"{base_url}api/v0/solutions/{solution_id}"
#     async with session.get(solution_url, cookies=cookies, headers={'X-Solve-Sync': 'true'}) as resp:
#         if resp.status == 200:
#             solution_data = await resp.json()
#             if not check_solution_exists(solution_data["scope_user"]["id"], solution_data["problem"]["id"]):
#                 print("="*50)
#                 print(f"Новое Accepted решение:")
#                 print(solution_data["problem"]["id"], solution_data["problem"]["statement"]["title"], '-', solution_data["scope_user"]["title"])
#                 save_solution_to_db(solution_data["scope_user"]["id"], solution_data["problem"]["id"])
#         else:
#             print(f"Не удалось получить решение {solution_id}: {resp.status}")

# asyncio.run(parse_accepted_solutions())

import requests
import json
from django.utils import timezone
from main.models import AcceptedSolution  # Замените 'main' на ваше приложение

import logging

logging.basicConfig(level=logging.INFO)

def parse_accepted_solutions():
    # Конфигурационные параметры
    SOLVE_URL = "https://solve.bsuir.by/"
    login = "denvilk"
    password = "Prodigy@Netw0rk"
    CONTEST_ID = 23  # ID соревнования

    # Аутентификация
    auth_url = f"{SOLVE_URL}/api/v0/login/"
    auth_resp = requests.post(auth_url, json={'login': login, 'password': password})

    if auth_resp.status_code != 201:
        print(f"Ошибка авторизации: {auth_resp.status_code} - {auth_resp.text}")
        return

    print("Успешная авторизация")
    cookies = auth_resp.cookies

    # Получаем поток событий
    event_feed_url = f"{SOLVE_URL}api/ccs/contests/{CONTEST_ID}/event-feed"
    with requests.get(event_feed_url, cookies=cookies, auth=(login, password), stream=True) as response:
        if response.status_code != 200:
            print(f"Ошибка получения event-feed: {response.status_code}")
            return

        print("Подключено к event-feed. Обработка данных...")
        buffer = ""

        for chunk in response.iter_content(chunk_size=1024):
            buffer += chunk.decode('utf-8')

            # Обрабатываем построчно
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.strip()

                if not line:
                    continue

                event = json.loads(line)
                if is_accepted_solution(event):
                    fetch_solution_details(cookies, SOLVE_URL, event)

def is_accepted_solution(event):
    """Проверяем, является ли событие Accepted решением"""
    return (
        event.get("type") == "judgements" and 
        event.get("data", {}).get("judgement_type_id") == "AC"
    )

def fetch_solution_details(cookies, base_url, event):
    """Получаем детали решения"""
    solution_id = event.get("data", {}).get("submission_id")
    if not solution_id:
        logging.warning("Отсутствует ID решения в событии")
        return

    solution_url = f"{base_url}api/v0/solutions/{solution_id}"
    resp = requests.get(solution_url, cookies=cookies, headers={'X-Solve-Sync': 'true'})

    if resp.status_code == 200:
        solution_data = resp.json()
        user_id = solution_data["scope_user"]["id"]
        problem_id = solution_data["problem"]["id"]
        title = solution_data["problem"]["statement"]["title"]
        user_title = solution_data["scope_user"]["title"]

        # Сохраняем в базу данных и получаем сохраненное решение
        saved_solution = AcceptedSolution.save_solution(user_id, problem_id, title, user_title)

        # Если решение было сохранено, выводим его
        if saved_solution:
            logging.info(f"Сохраненное решение: {saved_solution}")
    else:
        logging.error(f"Не удалось получить решение {solution_id}: {resp.status_code}")