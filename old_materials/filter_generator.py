# examples:
# 1. из описания: ?filter={"$and":[{"f_778clr1gcvp":5},{"f_offering_men_needed":{"$gt":0}}]}
# 2. из FireFox: {"$and":[{"f_offering_status":{"$eq":"2vi89elxqk9"}}]}
import datetime
import json
from typing import Any

TRANSLATE = {
    'f_offering_name': "Наименование вакансии",           # 1
    'createdAt': "Дата создания",                               # 2
    'updatedAt': "Дата обновления",                             # 3
    'f_min_age': "Минимальный возраст",                   # 4
    'f_offering_max_age': "Максимальный возраст",         # 5
    'f_offering_gender': "Пол",                           # 6
    'f_offering_min_price': "Минимальная оплата",         # 7
    'f_offering_max_price': "Максимальная оплата",        # 8
    'f_offering_men_needed': "Требуется мужчин",          # 9
    'f_offering_women_needed': "Требуется женщин",        # 10
    'f_offering_description': "Описание старое",          # 11
    'f_offering_new_description': "Описание новое",       # 12
    'f_778clr1gcvp': "Область",                           # 13
    'f_offering_nationality': "Гражданство",              # 14
    'f_offering_offering': "Категория работы",            # 15
    'f_offering_rate': "Оплата",                          # 16
}

POSSIBLE_FILTERS = {
        "createdAt": None,
        "updatedAt": None,
        "f_min_age": None,
        "f_offering_max_age": None,
        "f_offering_gender": None,
        "f_offering_min_price": None,
        "f_offering_max_price": None,
        "f_offering_men_needed": None,
        "f_offering_women_needed": None,
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


def generate_filter(filters: dict[str, str | None]) -> str:
    # out_string = '{"$and":[{"f_offering_status":{"$eq":"2vi89elxqk9"}}]}'
    # {"$and":[{"$and":[
    #   {"f_offering_nationality":
    #       {"$anyOf":["gcqez27y5f4","gk7e2465a07"]}
    #       }]},
    # {"$and":[{"f_offering_status":{"$eq":"2vi89elxqk9"}}]}]}

    out_string = '{"$and":[{%s}]}'
    filter_string = []
    for filter_name, value in filters.items():
        if value is None:
            continue
        if filter_name == "f_778clr1gcvp":
            filter_string.append(f'"$and":[{"{"}"{filter_name}":{"{"}')
            filter_string.append(f'"id":{"{"}"$eq":{int(value)}')
            filter_string.append('}}]}"')
        else:
            filter_string.append('"$and":')
            filter_string.append(f'[{"{"}"{filter_name}":{"{"}')
            tmp = ','.join(
                [f'"{ln}"' for ln in value]
            )
            filter_string.append(f'"$anyOf":[{tmp}]{"}}]}"}')

    filter_string.append(',{"$and":[{"f_offering_status":{"$eq":"2vi89elxqk9"}}]')
    out_string = out_string % ''.join(filter_string)
    return out_string


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
        case "М": return list(swap(GENDERS)["мужчина"])
        case "Ж": return list(swap(GENDERS)["женщина"])


def choose_category() -> list[str]:
    category_nums = list(CATEGORY.values())
    print("Выберите категорию")
    for i, c in enumerate(category_nums):
        print(f"{i}.\t{c}")
    while True:
        num = get_int()
        if 1 > num > len(category_nums):
            print("Неверный ввод.")
        else:
            return list(swap(CATEGORY)[category_nums[num - 1]])


def choose_rate() -> list[str]:
    rate = input("Выберите тип оплаты:\n1. Выработка\n2. Фикс\n_>:")
    match rate:
        case "1": return list(swap(OFFERING_RATE)["Выработка"])
        case "2": return list(swap(OFFERING_RATE)["Фикс"])


def choose_filters() -> dict[str, Any] | None:
    filters = {}
    count = 1
    for key in POSSIBLE_FILTERS.keys():
        print(f"{count}.\t{TRANSLATE.get(key)}")
        count += 1
    print(f'{0}.\tЗавершить')
    while True:
        filter_num = int(input("Введите номер фильтра: "))
        if filter_num == 0:
            return filters
        match filter_num:
            case 0: break
            case 1: filters["createdAt"] = get_date_time()
            case 2: filters["updatedAt"] = get_date_time()
            case 3: filters["f_min_age"] = get_int()
            case 4: filters["f_offering_max_age"] = get_int()
            case 5: filters["f_offering_gender"] = choose_gender()
            case 6: filters["f_offering_min_price"] = get_int()
            case 7: filters["f_offering_max_price"] = get_int()
            case 8: filters["f_offering_men_needed"] = get_int()
            case 9: filters["f_offering_women_needed"] = get_int()
            case 10: filters["f_offering_offering"] = choose_category()
            case 11: filters["f_778clr1gcvp"] = choose_places()
            case 12: filters["f_offering_nationality"] = choose_nationality()
            case 13: filters["f_offering_rate"] = choose_rate()

    return filters


def swap(params: dict[str, str]) -> dict[str, str]:
    return dict([*zip(params.values(), params.keys())])


if __name__ == '__main__':
    print(swap(GENDERS))
    print(swap(GENDERS)["мужчина"])
    print(result := choose_filters())
    expected = ('{"$and":[{"$and":['
                '{"f_offering_nationality":'
                '{"$anyOf":["gcqez27y5f4","gk7e2465a07"]}}]},'
                '{"$and":[{"f_offering_status":{"$eq":"2vi89elxqk9"}}]}]}')
    final = generate_filter(result)
    print(f'expected: {expected}')
    print(f'final:    {final}')
    print(final == expected)

