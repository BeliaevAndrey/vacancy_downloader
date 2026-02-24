import os
import json

import requests


API_URL = os.getenv("API_URL", "https://platform.vaxtarekrut.ru/api/")
API_KEY = os.getenv("API_KEY")


def get_headers() -> dict:
    if not API_KEY:
        raise RuntimeError("Переменная окружения API_KEY не установлена (загрузите .env).")
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "application/json",
    }


def get_regions() -> dict:
    """
    Тестовый запрос к /t_places (список регионов).
    """
    url = API_URL.rstrip("/") + "/t_places"
    params = {
        "pageSize": 50,
    }
    resp = requests.get(url, headers=get_headers(), params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def get_job_offerings_with_filters(region_id: int) -> dict:
    """
    Тестовый запрос к /t_job_offerings с фильтрами из описания API.

    Примеры из ТЗ:
    - By Region:        ?filter[f_778clr1gcvp]=
    - Men Needed:       ?filter[f_offering_men_needed][$gt]=0
    - Nationality:      ?filter[f_offering_nationality][$anyOf]=["<id-национальности>"]
    - Combined (пример): ?filter={"$and":[{"f_778clr1gcvp":5},{"f_offering_men_needed":{"$gt":0}}]}
    """
    url = API_URL.rstrip("/") + "/t_job_offerings"

    # Собираем комбинированный фильтр по примерам из описания API:
    # - регион
    # - требуются мужчины
    # - фильтр по национальности (пример — Узбекистан и Молдова)
    combined_filter = {
        "$and": [
            {"f_778clr1gcvp": region_id},
            {"f_offering_men_needed": {"$gt": 0}},
            {"f_offering_nationality": {"$anyOf": ["34ttqq61lvg", "sc291qbzdg3"]}},
        ]
    }

    params = {
        "pageSize": 50,
        # Передаём JSON‑строку в параметр filter
        "filter": json.dumps(combined_filter, separators=(",", ":")),
    }

    resp = requests.get(url, headers=get_headers(), params=params, timeout=30)
    print(f"Request URL: {resp.request.url}")
    print(f"Status code: {resp.status_code}")
    resp.raise_for_status()
    return resp.json()


def main() -> None:
    # 1. Получаем регионы, чтобы иметь валидный id региона
    regions_response = get_regions()
    regions = regions_response.get("data", [])

    print("=== Доступные регионы (первые 5) ===")
    for place in regions[:5]:
        print(f"id={place.get('id')}, name={place.get('f_places_name')}")

    if not regions:
        print("Не удалось получить список регионов.")
        return

    # Для теста берём id первого региона в списке.
    test_region_id = regions[0].get("id")
    print(f"\nИспользуем test_region_id={test_region_id} для фильтра.")

    # 2. Делаем тестовый запрос к вакансиям с комбинированным фильтром
    offerings = get_job_offerings_with_filters(test_region_id)

    print("\n=== Пример ответа по вакансиям (первые 3 записи) ===")
    for item in offerings.get("data", [])[:3]:
        print(
            f"ID={item.get('id')}, "
            f"Название={item.get('f_offering_name')}, "
            f"Мужчин нужно={item.get('f_offering_men_needed')}, "
            f"Регион ID={item.get('f_778clr1gcvp')}"
        )
    print("\nВсего вакансий:", offerings.get("meta", {}).get("totalCount", 0))


if __name__ == "__main__":
    main()

