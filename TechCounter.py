import queue
import re
import requests
import time
import threading

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
        self.queue = None

    def add_parasites(self, parasites):
        self._parasites += parasites

    def get_page(self, url, data=None):
        return requests.get(url=url, params=data).json()

    def get_words(self, vacancies):
        for vacancy in vacancies:
            if vacancy['archived']:
                continue
            url_vac = vacancy['url']
            resp_vac = self.get_page(url_vac)

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

    def get_words_and_rows(self, pages=100, start_page=0):
        start = time.time()
        print('page:')
        for page in range(start_page, pages):
            print(page + 1, end=' ')
            data_vac = {"specialization": "1", "area": self._city_code, 'page': page}

            resp_vac = self.get_page(url_vacancies, data_vac)
            vacancies = resp_vac['items']

            self.get_words(vacancies)

        print('Entire job took:', time.time()-start)
        return 'Ok'

    def get_page_from_queue(self):
        while True:
            page = self.queue.get()
            with self.lock:
                print(page['page'], end=' ')
            vacancies = page['items']
            self.get_words(vacancies)
            self.queue.task_done()

    def get_words_and_rows_with_threading(self, pages=100, start_page=0, threads=8):
        start_th = time.time()
        self.queue = queue.Queue(pages-start_page)
        self.lock = threading.Lock()

        print('page:')

        for _ in range(threads):
            th = threading.Thread(target=self.get_page_from_queue)
            th.daemon = True
            th.start()

        for page in range(start_page, pages):
            data_vac = {"specialization": "1", "area": self._city_code, 'page': page}
            self.queue.put(self.get_page(url_vacancies, data_vac))

        self.queue.join()

        print('Entire job took:', time.time()-start_th)
        return 'OK'

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
        l_word = max(len(x) for x in res_words)
        for key in res_words:
            print(key.ljust(l_word), '=>\t', [x for x,y in res_words[key].most_common(second_most_common)])

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
