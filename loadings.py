import csv


def load_results():
    global data
    with open('res.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=',', quotechar='"')
        data = list(reader)
