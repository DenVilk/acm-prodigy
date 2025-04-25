import json
import logging
import requests
from django.core.management.base import BaseCommand
from main.models import AcceptedSolution
from main.utils import Configuration

logger = logging.getLogger(__name__)


class SolveAuthorizationException(Exception):
    def __str__(self):
        return 'Cannot authenticate to solve'


class Command(BaseCommand):
    help = "Getting balloons"

    def __solve_authenticate(self, login, password):
        auth_url = f"{self.SOLVE_URL}/api/v0/login/"
        auth_resp = requests.post(
            auth_url,
            json={
                'login': login,
                'password': password,
            }
        )

        if auth_resp.status_code != 201:
            logger.critical(f"Ошибка авторизации: {auth_resp.status_code} - {auth_resp.text}")
            raise SolveAuthorizationException()

        return auth_resp.cookies

    def handle(self, *args, **options):
        self.SOLVE_URL = Configuration('configuration.solve.root_url')
        self.CONTEST_ID = Configuration('configuration.solve.balloons.contest_id')
        self.SOLVE_LOGIN = Configuration('configuration.solve.login')
        self.SOLVE_PASSWORD = Configuration('configuration.solve.password')

        self.__cookies = self.__solve_authenticate(
            self.SOLVE_LOGIN,
            self.SOLVE_PASSWORD,
        )

        while True:
            self.polling()

    def polling(self):
        event_feed_url = f"{self.SOLVE_URL}/api/ccs/contests/{self.CONTEST_ID}/event-feed"
        with requests.get(
            event_feed_url,
            cookies=self.__cookies,
            auth=(self.SOLVE_LOGIN, self.SOLVE_PASSWORD),
            stream=True,
        ) as response:

            if response.status_code != 200:
                logging.error(f"Ошибка получения event-feed: {response.status_code}")
                return

            logging.info("Подключено к event-feed. Обработка данных...")
            buffer = ""

            for chunk in response.iter_content(chunk_size=1024):
                buffer += chunk.decode('utf-8')

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()

                    if not line:
                        continue

                    event = json.loads(line)
                    if self.is_accepted_solution(event):
                        self.fetch_solution_details(event)

    def is_accepted_solution(self, event) -> bool:
        """Проверяем, является ли событие Accepted решением"""
        return event.get("type") == "judgements" and \
               event.get("data", {}).get("judgement_type_id") == "AC"

    def fetch_solution_details(self, event):
        """Получаем детали решения"""
        solution_id = event.get("data", {}).get("submission_id")
        if not solution_id:
            logging.warning("Отсутствует ID решения в событии")
            return

        solution_url = f"{self.SOLVE_URL}/api/v0/solutions/{solution_id}"
        resp = requests.get(solution_url, cookies=self.__cookies, headers={'X-Solve-Sync': 'true'})

        if resp.status_code == 200:
            solution_data = resp.json()
            user_id = solution_data["scope_user"]["id"]
            problem_id = solution_data["problem"]["id"]
            title = solution_data["problem"]["statement"]["title"]
            user_title = solution_data["scope_user"]["title"]

            saved_solution = AcceptedSolution.save_solution(user_id, problem_id, title, user_title)

            if saved_solution:
                logging.info(f"Сохраненное решение: {saved_solution}")
        else:
            logging.error(f"Не удалось получить решение {solution_id}: {resp.status_code}")