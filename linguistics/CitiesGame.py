import random
from collections import defaultdict


class CitiesGameException(Exception):
    pass


class WrongStartLetterException(CitiesGameException):
    def __init__(self, letter):
        self.letter = letter

    def __str__(self):
        return "Назовите город на букву " + self.letter.upper()


class CityUsedException(CitiesGameException):
    def __str__(self):
        return "Город уже был использован"


class CityMismatchException(CitiesGameException):
    def __str__(self):
        return "Города нет в нашей базе. Назовите другой город"


ALPHABET = list("абвгдеёжзийклмнопрстуфхцчшщъыьэюя")


class CitiesGame:
    def __init__(self, database):
        self.available = defaultdict(set)
        with open(database) as f:
            for city in f:
                city = city.strip()
                if city:
                    self.available[city[0]].add(city)
        self.bad_start_letters = set(ALPHABET) - self.available.keys()
        self.used = set()
        self.last_letter = ""
        self.is_ended = False

    def get_last_letter(self, city):
        assert len(city) > 1, "Name of the city is too short"
        return city[-1] if city[-1] not in self.bad_start_letters else city[-2]

    def get_answer(self, city):
        if not city or city[0] != self.last_letter:
            raise WrongStartLetterException(self.last_letter)
        if city in self.used:
            raise CityUsedException()
        if city not in self.available[city[0]]:
            raise CityMismatchException()

        self.used.add(city)
        cities = self.available[self.get_last_letter(city)]
        if cities:
            return self._next_city(cities)
        else:
            self.is_ended = True

    def start(self):
        cities = random.choice(list(self.available.values()))
        return self._next_city(cities)

    def _next_city(self, cities):
        city = random.sample(cities, 1)[0]
        cities.remove(city)
        self.used.add(city)
        self.last_letter = self.get_last_letter(city)
        if not self.available[self.last_letter]:
            self.is_ended = True
        return city.title()


if __name__ == "__main__":
    game = CitiesGame("ru_cities")
    print("Поиграем в города?")
    print(game.start())
    while not game.is_ended:
        city = input().lower().strip()
        if city:
            try:
                answer = game.get_answer(city)
                if answer:
                    print(answer)
                else:
                    print("Поздравляем с победой!")
            except CitiesGameException as e:
                print(e)
    print("Города закончились. Спасибо за веселую игру!")
