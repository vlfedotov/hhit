import re
import requests
from collections import defaultdict
from collections import Counter

from .config import *


class TechCounter(object):
    cities = {'SPB': 2,
              'MSK': 1}

    def __init__(self, city):
        self.city = city
        self._city_code = TechCounter.cities[city]
        self.description_rows = []
        self.name_rows = []
        self.description_all_words = Counter()
        self.name_all_words = Counter()
        self._tech_names_pat = re.compile(r'([A-Z][A-Za-z\+\.]*)')
        self._parasites = {'experience', 'it', 'we', 'english', 'ms', 'the', 'work', 'knowledge', 'petersburg',
                          'strong', 'office', 'you', 'at', 'us', 'flexible', 'working', 'engineer', 'saint',
                          'what', 'required', 'education', 'good', 'responsibilities', 'please', 'medical',
                          'russian', }

    def add_parasites(self, parasites):
        self._parasites += parasites

    def get_words_and_rows(self, pages=100, start_page=0):
        print('page:')
        for page in range(start_page, pages):
            print(page + 1, end=' ')
            data_vac = {"specialization": "1", "area": self._city_code, 'page': page}

            resp_vac = requests.get(url=url_vacancies, params=data_vac).json()
            vacancies = resp_vac['items']

            for vacancy in vacancies:
                if not vacancy['archived']:
                    url_vac = vacancy['url']
                    resp_vac = requests.get(url=url_vac).json()

                    desc = set()
                    name = set()

                    try:
                        desc_raw = self._tech_names_pat.findall(resp_vac['description'])
                        for d in desc_raw:
                            desc.add(d.rstrip('.').lower())
                        desc -= self._parasites
                    except KeyError as e:
                        print('no desc', end=' ')

                    try:
                        name_raw = self._tech_names_pat.findall(resp_vac['name'])
                        for n in name_raw:
                            name.add(n.rstrip('.').lower())
                        name -= self._parasites
                    except KeyError as e:
                        print('no name', end=' ')

                    if desc:
                        self.description_rows.append(desc)
                        self.description_all_words.update(desc)
                    if name:
                        self.name_rows.append(name)
                        self.name_all_words.update(name)

        return 'Ok'

    def get_int_combinations(self, int_words):
        res_words = defaultdict(Counter)

        for row in self.description_rows:
            for word in int_words:
                if word in row:
                    row_tmp = row - {word}
                    res_words[word].update(row_tmp)

        return res_words

    def show_int_combinations(self, first_most_common=20, second_most_common=10):
        ints = [x for x,y in self.description_all_words.most_common(first_most_common)]
        res_words = self.get_int_combinations(ints)
        for key in res_words:
            print(key, '\r\t\t=>\t', [x for x,y in res_words[key].most_common(second_most_common)])

    def delete_parasites(self, parasites):
        self._parasites.add(parasites)
        for par in self._parasites:
            for row in self.description_rows:
                row -= par
            for row in self.name_rows:
                row -= par

            parasite = {par: self.description_all_words[par]}
            description_all_words.subtract(parasite)
            parasite = {par: self.name_all_words[par]}
            name_all_words.subtract(parasite)
