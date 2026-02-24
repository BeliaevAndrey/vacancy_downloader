import json
import os
from bs4 import BeautifulSoup

import requests

from typing import Any

API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")
JOBS_DATA = "t_job_offerings"
JOBS_PLACES = "t_places"
RESULTS_PATH = "results"
RESULTS_NAME = "results.json"

NATIONALITY = {
    "gcqez27y5f4": "РФ",
    "34ttqq61lvg": "Узбекистан",
    "gk7e2465a07": "Белоруссия",
    "kl361vufv57": "Таджикистан",
    "sc291qbzdg3": "Молдова",
    "ntk2lrx6fex": "Армения",
    "111501hylor": "Азербайджан",
    "mng5b3rqyq0": ("Дагестан | Ингушетия | Кабардино-Балкария "
                    "| Карачаево-Черкессия | Чечня | Адыгея | Алания "
                    "| Кавказский федеральный округ | Абхазия | Осетия"),

}


# # def generate_filter(filters: dict[str, Any]) -> str:
#     out_string = '{"$and":[{%s}]}'
#     filter_string = []
#     for filter_name, value in filters.items():
#         if value is None:
#             continue
#         if filter_name == "f_778clr1gcvp":
#             filter_string.append('"$and":[{"f_offering_city":{')
#             filter_string.append(f'"id":{"{"}"$eq":{int(value)}')
#             filter_string.append('}}]}"')
#         else:
#             filter_string.append('"$and":')
#             filter_string.append(f'[{"{"}"{filter_name}":{"{"}')
#             tmp = ','.join([f'"{ln}"' for ln in value])
#             filter_string.append(f'"$anyOf":[{tmp}]{"}}]}"}')
# 
#     filter_string.append(',{"$and":[{"f_offering_status":{"$eq":"2vi89elxqk9"}}]')
#     ff: dict = {
#         "$and":
#             [
#                 {"$and":
#                     [
#                         {"f_offering_nationality": {
#                             "$anyOf": ["mng5b3rqyq0"]
#                         }
#                         }
#                     ]},
#                 {
#                     "$and":
#                         [
#                             {"f_offering_status": {"$eq": "2vi89elxqk9"}
#                              }
#                         ]
#                 }
#             ]
#     }
#     out_string = out_string % ''.join(filter_string)
#     return out_string


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


def get_filtered_data() -> dict[str, Any] | None:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "application/json",
    }
    # 1. из описания: ?filter={"$and":[{"f_778clr1gcvp":5},{"f_offering_men_needed":{"$gt":0}}]}
    # 2. из FireFox: {"$and":[{"f_offering_status":{"$eq":"2vi89elxqk9"}}]}
    # current_filter = generate_filter(filter_param)
    # current_filter = {'$and': [
    #     {'$and': [{'f_offering_city': {'id': {'$eq': 19}}}]},
    #     {'$and': [{'f_offering_men_needed': {'$gt': 1}}]},
    #     {"$and": [{"f_offering_status":{"$eq":"2vi89elxqk9"}}]}
    # ]}
    # region_id = 8
    # current_filter = {
    #     "$and": [
    #         {"f_778clr1gcvp": region_id},
    #         {"f_offering_men_needed": {"$gt": 0}},
    #         {"f_offering_nationality": {"$anyOf": ["34ttqq61lvg", "sc291qbzdg3"]}},
    #     ]
    # }
    current_filter = {
        "$and": [
            {
                "$and": [
                    {
                        "f_offering_gender": {
                            "$anyOf": [
                                "q3slmijbifh"
                            ]
                        }
                    },
                    {
                        "f_offering_men_needed": {
                            "$gte": 1
                        }
                    },
                    {
                        "f_offering_city": {
                            "id": {
                                "$eq": 8
                            }
                        }
                    },
                    {
                        "f_offering_nationality": {
                            "$anyOf": [
                                "gk7e2465a07",
                                "sc291qbzdg3",
                                "111501hylor"
                            ]
                        }
                    },
                    {
                        "f_offering_rate": {
                            "$eq": "0xzahoxb7p6"
                        }
                    },
                    {
                        "f_offering_max_age": {
                            "$gte": 33
                        }
                    }
                ]
            },
            {
                "$and": [
                    {
                        "f_offering_status": {
                            "$eq": "2vi89elxqk9"
                        }
                    }
                ]
            }
        ]
    }

    params = {
        "pageSize": 120,
        "filter": json.dumps(current_filter, separators=(",", ":"))
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
        "v_nationality": "Гражданство",
        "v_category": "Категория работы",
        "v_rate": "Оплата",
    }
    for key, value in data.items():
        print(f"ID: {key}")
        for i_key, i_value in value.items():
            print(f"{translate[i_key]}: {i_value}")
        print(f"\n{'=' * 40}\n")


def get_vacancy_description(data: dict[str, Any], places: list[dict[str, Any]] = None) -> dict[int, dict[str, Any]]:
    descriptions = {}
    genders = {"08i2iwrzqi2": "женщина", "q3slmijbifh": "мужчина"}
    category = {"m686ynzq3hk": "Склад", "egphzfob65p": "Производство"}
    offering_rate = {"0xzahoxb7p6": "Выработка", "yumhk3a93le": "Фикс"}
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
            "v_min_price": vacancy_card.get("f_offering_min_price", "Не указано"),
            "v_max_price": vacancy_card.get("f_offering_max_price"),
            "v_men_needed": vacancy_card.get("f_offering_men_needed"),
            "v_women_needed": vacancy_card.get("f_offering_women_needed"),
            "v_category": category.get(vacancy_card.get("f_offering_offering"), "Другое"),
            "v_rate": offering_rate.get("f_offering_rate", "Не обозначено")
        }

        if genders_needed is not None:
            descriptions[key].update({"v_gender": ", ".join([genders[g] for g in genders_needed])})

        descriptions[key]["v_nationality"] = [NATIONALITY.get(n) for n in vacancy_card.get("f_offering_nationality")]

        if places is not None:
            id_num = vacancy_card.get("f_778clr1gcvp")
            descriptions[key]["v_region"] = get_place(id_num, places)
        else:
            descriptions[key]["v_region"] = "Unknown"

        soup = BeautifulSoup(vacancy_card.get("f_offering_new_description"), "html5lib")
        descriptions[key]["v_desc"] = soup.getText(separator="\n", strip=True)

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
    # data: dict = get_filtered_data({'f_778clr1gcvp': 19})
    # data: dict = get_filtered_data({'f_offering_nationality': ['gcqez27y5f4', 'gk7e2465a07']})
    data: dict = get_filtered_data()
    # data: dict = get_filtered_data({'f_offering_nationality': ['mng5b3rqyq0']})
    # data: dict = get_data()
    dump_intermediate(data, "downloaded.json")
    dump_intermediate(places_response, "places.json")
    if data.get("data"):
        result = get_vacancy_description(data, places)
        dump_results(result)
    else:
        print("Не найдено вакансий")
    print("=" * 40)
    print(data.get("meta"))


if __name__ == '__main__':
    if check_path():
        run()
