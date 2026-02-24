import json
import os
import pprint
from bs4 import BeautifulSoup

import requests

from typing import Any

API_URL = "https://platform.vaxtarekrut.ru/api/"
JOBS_DATA = "t_job_offerings"
JOBS_PLACES = "t_places"
API_KEY = os.getenv("API_KEY")
RESULTS_PATH = "results"
RESULTS_NAME = "results.json"

NATIONALITY = {
    'mng5b3rqyq0': ('Дагестан | Ингушетия | Кабардино-Балкария '
                    '| Карачаево-Черкессия | Чечня | Адыгея | Алания '
                    '| Кавказский федеральный округ | Абхазия | Осетия'),
    'gcqez27y5f4': 'РФ',
    '34ttqq61lvg': 'Узбекистан',
    'gk7e2465a07': 'Белоруссия',
    'kl361vufv57': 'Таджикистан',
    'sc291qbzdg3': 'Молдова',
    'ntk2lrx6fex': 'Армения',
    '111501hylor': 'Азербайджан'}


def check_path() -> bool:
    try:
        if not os.path.isdir(RESULTS_PATH):
            os.mkdir(RESULTS_PATH)
        return True
    except Exception as err:
        print(err)
        return False


def get_places() -> dict[str, Any]:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "application/json",
    }
    params = {
        "pageSize": 120
    }
    data = requests.get(f"{API_URL}{JOBS_PLACES}", headers=headers, params=params)
    return data.json()


def get_place(id_num: int, places: list) -> str:
    for place in places:
        if place.get("id") == id_num:
            return place.get("f_places_name")
    return f"Область с id {id_num} не найдена."


def get_data() -> dict[str, Any]:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "application/json",
    }

    params = {
        "pageSize": 120
    }

    data = requests.get(f"{API_URL}{JOBS_DATA}", headers=headers, params=params)
    return data.json()


def print_dict(data: [list, str, dict[str, Any]]) -> None:
    translate = {
        "v_name": "Наименование вакансии",
        "v_createdAt": "Создано",
        "v_updatedAt": "Обновлено",
        "v_min_age": "Минимальный возраст",
        "v_max_age": "Максимальный возраст",
        "v_gender": "Пол",
        "v_min_price": "Минимальная оплата",
        "v_max_price": "Максимальная оплата",
        "v_men_needed": "Требуется мужчин",
        "v_women_needed": "Требуется женщин",
        "v_desc": "Описание",
        "v_region": "Область",

    }
    for key, value in data.items():
        print(f"ID: {key}")
        if isinstance(value, dict):
            for i_key, i_value in value.items():
                print(f"{translate[i_key]}: {i_value}")
        else:
            print("\033[31m", value, "\033[0m", sep="")
        print(f"\n{'=' * 40}\n")


def get_vacancy_description(data: dict[str, Any], places: list[dict[str, Any]] = None) -> dict[int, dict[str, Any]]:
    descriptions = {}
    genders = {"08i2iwrzqi2": "Женщина", "q3slmijbifh": "Мужчина"}
    for vacancy_card in data.get("data"):
        key = vacancy_card.get("id")
        genders_needed = vacancy_card.get("f_offering_gender")
        descriptions[vacancy_card.get("id")] = {
            "v_name": vacancy_card.get("f_offering_name"),
            "v_createdAt": vacancy_card.get("createdAt"),
            "v_updatedAt": vacancy_card.get("updatedAt"),
            "v_min_age": vacancy_card.get("f_min_age"),
            "v_max_age": vacancy_card.get("f_offering_max_age"),
            "v_gender": None,
            "v_min_price": vacancy_card.get("f_offering_min_price"),
            "v_max_price": vacancy_card.get("f_offering_max_price"),
            "v_men_needed": vacancy_card.get("f_offering_men_needed"),
            "v_women_needed": vacancy_card.get("f_offering_women_needed"),
        }

        soup = BeautifulSoup(vacancy_card.get("f_offering_new_description"), "html5lib")
        descriptions[key]["v_desc"] = soup.getText(separator="\n", strip=True)

        if places is not None:
            id_num = vacancy_card.get("f_778clr1gcvp")
            descriptions[key]["v_region"] = get_place(id_num, places)
        if genders_needed is not None:
            descriptions[key].setdefault("v_gender", ", ".join([genders[g] for g in genders_needed]))

    return descriptions


def dump_results(results: dict[int, Any]) -> None:
    path = os.path.join(RESULTS_PATH, RESULTS_NAME)
    with open(path, "w", encoding="utf-8") as fo:
        json.dump(results, fo, indent=4, ensure_ascii=False)


def dump_intermediate(results: dict[Any, Any], file_name: str) -> None:
    if not os.path.isdir("tmp"):
        os.mkdir("tmp")

    path = os.path.join("tmp", file_name)
    with open(path, "w", encoding="utf-8") as fo:
        json.dump(results, fo, indent=4, ensure_ascii=False)


def run():
    places_response = get_places()
    places = places_response.get("data")
    data: dict = get_data()
    dump_intermediate(data, "downloaded.json")
    dump_intermediate(places_response, "places.json")
    result = get_vacancy_description(data, places)
    print_dict(result)
    print("=" * 40)
    print("=" * 40)
    print(data.get("meta"))
    print("=" * 40)
    print(places_response.get("meta"))
    dump_results(result)


if __name__ == '__main__':
    pprint.pp(NATIONALITY)
    # if check_path():
    #     run()
