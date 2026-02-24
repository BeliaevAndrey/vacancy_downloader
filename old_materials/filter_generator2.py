# examples:
# 1. из описания: ?filter={"$and":[{"f_778clr1gcvp":5},{"f_offering_men_needed":{"$gt":0}}]}
# 2. из FireFox: {"$and":[{"f_offering_status":{"$eq":"2vi89elxqk9"}}]}
import datetime
import json
from typing import Any

TRANSLATE = {
    'f_offering_name': "Наименование вакансии",  # 1
    'createdAt': "Дата создания",  # 2
    'updatedAt': "Дата обновления",  # 3
    'f_min_age': "Минимальный возраст",  # 4
    'f_offering_max_age': "Максимальный возраст",  # 5
    'f_offering_gender': "Пол",  # 6
    'f_offering_min_price': "Минимальная оплата",  # 7
    'f_offering_max_price': "Максимальная оплата",  # 8
    'f_offering_men_needed': "Требуется мужчин",  # 9
    'f_offering_women_needed': "Требуется женщин",  # 10
    'f_offering_description': "Описание старое",  # 11
    'f_offering_new_description': "Описание новое",  # 12
    'f_778clr1gcvp': "Область",  # 13
    'f_offering_nationality': "Гражданство",  # 14
    'f_offering_offering': "Категория работы",  # 15
    'f_offering_rate': "Оплата",  # 16
}

POSSIBLE_FILTERS = {
    # "createdAt": None,
    # "updatedAt": None,
    # "f_min_age": None,
    "f_offering_max_age": None,
    "f_offering_gender": None,
    # "f_offering_min_price": None,
    # "f_offering_max_price": None,
    # "f_offering_men_needed": None,
    # "f_offering_women_needed": None,
    "f_offering_offering": None,
    "f_778clr1gcvp": None,
    "f_offering_nationality": None,
    "f_offering_rate": None,

}

GENDERS = {"08i2iwrzqi2": "женщина", "q3slmijbifh": "мужчина"}
CATEGORY = {"m686ynzq3hk": "Склад", "egphzfob65p": "Производство"}
OFFERING_RATE = {"0xzahoxb7p6": "Выработка", "yumhk3a93le": "Фикс"}
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

with open("tmp/places.json", "r", encoding="utf-8") as fi:
    places = json.load(fi)


def generate_filter(filters: dict[str, Any]) -> dict[str, Any]:
    """
    Построение фильтра в формате, максимально приближенном к примеру из браузера.

    Структура целевого фильтра:
    {
        "$and": [
            {
                "$and": [
                    { ... основные условия ... },
                    { "f_offering_city": { "id": { "$eq": <region_id> } } },
                    ...
                ]
            },
            {
                "$and": [
                    { "f_offering_status": { "$eq": "2vi89elxqk9" } }
                ]
            }
        ]
    }
    """
    main_conditions: list[dict[str, Any]] = []

    for key, value in filters.items():
        if value is None:
            continue

        # Область: как в примере из браузера — через f_offering_city.id.$eq
        if key == "f_778clr1gcvp" and isinstance(value, int):
            main_conditions.append(
                {
                    "f_offering_city": {
                        "id": {
                            "$eq": value
                        }
                    }
                }
            )
            continue

        # Числа (возраст, количество и т.п.) — как в примере: $gte
        if isinstance(value, int):
            main_conditions.append({key: {"$gte": value}})
        # Строки (даты в ISO и пр.) — тоже через $gte
        elif isinstance(value, str):
            main_conditions.append({key: {"$gte": value}})
        # Списки кодов: национальность, пол, категория, тип оплаты и др.
        elif isinstance(value, list):
            # Категория работы в примере идёт через "$in"
            if key == "f_offering_offering":
                main_conditions.append({key: {"$in": value}})
            # Тип оплаты выбирается в единственном варианте — используем "$eq"
            elif key == "f_offering_rate" and len(value) == 1:
                main_conditions.append({key: {"$eq": value[0]}})
            # Пол: добавляем ограничение по количеству людей этого пола
            elif key == "f_offering_gender":
                main_conditions.append({key: {"$anyOf": value}})
                # мужской код: "q3slmijbifh", женский: "08i2iwrzqi2"
                if "q3slmijbifh" in value:
                    main_conditions.append({"f_offering_men_needed": {"$gte": 1}})
                if "08i2iwrzqi2" in value:
                    main_conditions.append({"f_offering_women_needed": {"$gte": 1}})
            else:
                main_conditions.append({key: {"$anyOf": value}})

    # "Хвост" со статусом — отдельный $and, как в запросе из браузера
    status_block = {
        "$and": [
            {
                "f_offering_status": {
                    "$eq": "2vi89elxqk9"
                }
            }
        ]
    }

    return {
        "$and": [
            {"$and": main_conditions},
            status_block,
        ]
    }


def get_date_time():
    prompt = "Введите дату в формате YYYY-MM-DD:"
    date_string = input(prompt)
    try:
        date_filter = datetime.datetime.strptime(date_string, "%Y-%m-%d")
        return date_filter.isoformat()
    except ValueError:
        print("Неверно введена дата. Проверьте формат: ГОД-МЕСЯЦ-ЧИСЛО")


def get_int():
    prompt = "Введите целое число:\n_> "
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Введите, пожалуйста, число.")


def choose_places() -> int:
    print("Выберите область")
    for d in places.get("data"):
        print(f'{d.get("id")}\t{d.get("f_places_name")}')
    print("Выбрать (0 -- завершить): ")
    place_id = get_int()
    return place_id


def choose_nationality() -> list[str]:
    nation_nums = list(NATIONALITY.values())
    chosen = []
    print("Выберите гражданство:")
    for i, nation in enumerate(nation_nums, start=1):
        print(f"{i}.\t{nation}")
    while True:
        print("Добавить (0 -- завершить)")
        num = get_int()
        print(f"{len(nation_nums)=} {num > len(nation_nums)}")
        if num == 0:
            break
        elif 0 > num or num > len(nation_nums):
            print("Неверный ввод.")
        else:
            chosen.append(swap(NATIONALITY)[nation_nums[num - 1]])
    return chosen


def choose_gender() -> list[str]:
    gender = input("Выберите пол: М, Ж\n_> ")
    match gender:
        case "М":
            return [swap(GENDERS)["мужчина"]]
        case "Ж":
            return [swap(GENDERS)["женщина"]]


def choose_category() -> list[str]:
    category_nums = list(CATEGORY.values())
    print("Выберите категорию")
    for i, c in enumerate(category_nums, start=1):
        print(f"{i}.\t{c}")
    while True:
        num = get_int()
        if num < 1 or num > len(category_nums):
            print("Неверный ввод.")
        else:
            return [swap(CATEGORY)[category_nums[num - 1]]]


def choose_rate() -> list[str]:
    rate = input("Выберите тип оплаты:\n1. Выработка\n2. Фикс\n_>:")
    match rate:
        case "1":
            return [swap(OFFERING_RATE)["Выработка"]]
        case "2":
            return [swap(OFFERING_RATE)["Фикс"]]


def choose_filters() -> dict[str, Any] | None:
    filters = {}
    count = 0
    filters_list = ["exit"] + list(POSSIBLE_FILTERS.keys())
    
    for key in filters_list:
        print(f"{count}.\t{TRANSLATE.get(key)}")
        count += 1
    print(f'{0}.\tЗавершить')
    while True:
        filter_num = int(input("Введите номер фильтра: "))
        if filter_num == 0:
            return filters
        match filters_list[filter_num - 1]:
            case "exit":
                break
            case "f_offering_max_age":
                filters["f_offering_max_age"] = get_int()
            case "f_offering_gender":
                filters["f_offering_gender"] = choose_gender()
            case "f_offering_offering":
                filters["f_offering_offering"] = choose_category()
            case "f_778clr1gcvp":
                filters["f_778clr1gcvp"] = choose_places()
            case "f_offering_nationality":
                filters["f_offering_nationality"] = choose_nationality()
            case "f_offering_rate":
                filters["f_offering_rate"] = choose_rate()

    return filters


def swap(params: dict[str, str]) -> dict[str, str]:
    return dict([*zip(params.values(), params.keys())])


if __name__ == '__main__':
    result = choose_filters()
    final = generate_filter(result)
    print("Собранный фильтр:")
    print(json.dumps(final, ensure_ascii=False, indent=4))
