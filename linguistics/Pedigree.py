# -*- coding: utf-8 -*-
import pytest

from enum import Enum

# Из приведенных тестов я сделала вывод, что братья и сестры бывают
# только родными в пределах задания.
# Если у жены есть ребенок, то и у мужа он тоже есть.
# Однополых браков у нас не существует :-)
# Если есть брат и сестра, и у каждого по разному родителю - это муж и жена.
# Обработку некорректных данных я толком не делала.
# Имена всех людей должны быть различны.
# Про внуков и дедушек можно спросить, но нельзя добавить такую информацию.


class Gender(Enum):
    unknown = 0
    male = 1
    female = 2


class Person(object):
    name_generator = 0

    def __init__(self, name=None, gender=Gender.unknown):
        # Есть вымышленные персонажи, облегчающие переходы по дереву
        # У каждого настоящего человека всегда есть какой-нибудь отец
        self.real = True if name else False
        if not name:
            name = str(Person.name_generator)
            Person.name_generator += 1
        self.name = name
        self.gender = gender
        self.spouse = None
        self.children = set()
        # Возможно, код стал бы легче, если бы мы хранили 2 переменные -
        # мать и отца. Но бывают ситуации, когда неизвестен пол родителя.
        self.parents = set()

    def __hash__(self):
        return self.name.__hash__()

    def replace_to_true_parent(self, new_parent, other=None):
        for parent in self.parents:
            if not parent.real:
                new_parent.children.update(parent.children)
                for child in parent.children:
                    child.parents = {new_parent}
        # Удаляем вымышленного отца: больше он не нужен
        self.parents = {parent for parent in self.parents if parent.real}
        self.parents.add(new_parent)
        if other:
            self.parents.add(other)

    def add_parent(self, parent):
        self.replace_to_true_parent(parent)
        if parent.spouse:
            self.parents.add(parent.spouse)
        if len(self.parents) == 2:
            a, b = self.parents
            a.spouse, b.spouse = b, a
            a.try_set_opposite_gender(b)
            b.try_set_opposite_gender(a)

    def try_set_opposite_gender(self, other):
        if other.gender != Gender.unknown:
            if other.gender == Gender.male:
                self.gender = Gender.female
            else:
                self.gender = Gender.male

    def set_parent_to_children(self, parent):
        for child in self.children:
            child.parents = {self, parent}

    def add_link(self, other, rel_type):
        if rel_type in ["child", "son", "daughter"]:
            self.add_parent(other)
            other.children.add(self)
        elif rel_type in ["parent", "father", "mother"]:
            self.children.add(other)
            other.add_parent(self)
        elif rel_type in ["husband", "wife"]:
            self.spouse, other.spouse = other, self
            self.set_parent_to_children(other)
            other.set_parent_to_children(self)
        elif rel_type in ["brother", "sister"]:
            first, *second = self.parents
            # Если первый настоящий - второй 100% настоящий
            if first.real:
                other.replace_to_true_parent(*self.parents)
            o_first, *o_second = other.parents
            self.replace_to_true_parent(*other.parents)
            # Достаточно обновить детей лишь у одного родителя, так как
            # При запросе мы все равно всегда объединяем множества.
            o_first.children.update({self, other})
        else:
            raise Exception("Unknown relation type: " + rel_type)

    def update_gender(self, gender):
        if gender != Gender.unknown:
            self.gender = gender
            if self.spouse:
                self.spouse.try_set_opposite_gender(self)

    def parent_request_helper(self, gender=Gender.unknown):
        if gender == Gender.unknown:
            return [parent.name for parent in self.parents]
        for parent in self.parents:
            if parent.gender == gender:
                return [parent.name]
        return []

    def parent_request(self, gender):
        return ", ".join(self.parent_request_helper(gender))

    def get_children(self, gender):
        children = set()
        for child in self.children:
            if gender in (child.gender, Gender.unknown):
                children.add(child.name)
            elif child.gender == Gender.unknown:
                children.add(child.name + "?")
        return children

    def child_request_helper(self, gender=Gender.unknown):
        children = self.spouse.get_children(gender) if self.spouse else set()
        return children | self.get_children(gender)

    def child_request(self, gender):
        return ", ".join(self.child_request_helper(gender))

    def sibling_request(self, gender):
        siblings = set()
        for parent in self.parents:
            siblings.update(parent.get_children(gender))
        siblings.discard(self.name)
        siblings.discard(self.name + "?")
        return ", ".join(siblings)

    def spouse_request(self, gender):
        if self.spouse:
            ending = "" if self.spouse.gender == gender else "?"
            return self.spouse.name + ending


class PedigreeHolder:
    DEFAULT_ANSWER = "Don't know"

    def __init__(self):
        self.people = {}

    def add(self, statement):
        who, _, whose, rel = statement.split()
        assert whose.endswith("'s")
        self.add_relative(who, whose[:-2], rel)

    def request(self, question):
        req_parts = question.split()
        if req_parts[0] == "Is" and req_parts[2] == "a":
            return self.gender_request(req_parts[1], req_parts[3][:-1])
        if question.startswith("Who is ") and req_parts[2].endswith("'s"):
            return self.relative_request(req_parts[2][:-2], req_parts[3][:-1])
        raise Exception("Unknown request type")

    def create_or_update(self, name, gender):
        if name not in self.people:
            self.people[name] = Person(name, gender)
            # У каждого человека есть отец! :-)
            self.people[name].add_link(Person(), "child")
        else:
            self.people[name].update_gender(gender)

    def add_relative(self, who_name, whose_name, rel_type):
        who_gender, whose_gender = self.get_genders_by_reltype(rel_type)
        self.create_or_update(who_name, who_gender)
        self.create_or_update(whose_name, whose_gender)
        self.people[who_name].add_link(self.people[whose_name], rel_type)

    def relative_request(self, name, rel_type):
        if name not in self.people:
            return self.DEFAULT_ANSWER
        person = self.people[name]
        gender, _ = self.get_genders_by_reltype(rel_type)
        if rel_type in ["parent", "father", "mother"]:
            return person.parent_request(gender) or self.DEFAULT_ANSWER
        if rel_type in ["child", "son", "daughter"]:
            return person.child_request(gender) or self.DEFAULT_ANSWER
        if rel_type in ["husband", "wife"]:
            return person.spouse_request(gender) or self.DEFAULT_ANSWER
        if rel_type in ["brother", "sister"]:
            return person.sibling_request(gender) or self.DEFAULT_ANSWER
        if rel_type in ["grandchild", "grandson", "granddaughter"]:
            ans = set()
            children = person.child_request_helper()
            for child in children:
                ans.update(self.people[child].child_request_helper(gender))
            return ", ".join(ans) or self.DEFAULT_ANSWER
        if rel_type in ["grandfather", "grandmother"]:
            ans = set()
            parents = person.parent_request_helper()
            for parent in parents:
                ans.update(self.people[parent].parent_request_helper(gender))
            return ", ".join(ans) or self.DEFAULT_ANSWER

    def gender_request(self, name, gender_word):
        if name not in self.people:
            return self.DEFAULT_ANSWER

        gender = self.people[name].gender
        if gender == Gender.unknown:
            return self.DEFAULT_ANSWER
        asked = Gender.male if gender_word == "man" else Gender.female
        return "Yes" if gender == asked else "No"

    @staticmethod
    def get_genders_by_reltype(rel_type):
        if rel_type == "husband":
            return Gender.male, Gender.female
        if rel_type == "wife":
            return Gender.female, Gender.male
        if rel_type in ["mother", "daughter", "sister", "grandmother",
                        "granddaughter"]:
            return Gender.female, Gender.unknown
        if rel_type in ["father", "son", "brother", "grandson", "grandfather"]:
            return Gender.male, Gender.unknown
        return Gender.unknown, Gender.unknown


aph = PedigreeHolder()
aph.add("Carol is Ann's sister")
aph.add("Ann is Brett's sister")
aph.add("Darren is Brett's father")
print(aph.request("Who is Ann's father?"))


ph = PedigreeHolder()
ph.add("Carol is Ann's daughter")
ph.add("Ann is Brett's wife")
ph.add("Darren is Brett's son")
ph.add("Brett is Darren's father")
ph.add("Carol is Frank's sister")
ph.add("Emily is Carol's daughter")
ph.add("Nathan is Emily's brother")
ph.add("John is Emily's brother")
ph.add("Filmore is Jeremy's son")
ph.add("Filmore is Lily's son")


@pytest.mark.parametrize("question, answer", [
    ("Is Carol a woman?", "Yes"),
    ("Is Frank a man?", "Don't know"),
    ("Is Brett a woman?", "No"),
    ("Who is Rose's father?", "Don't know"),
    ("Who is Brett's father?", "Don't know"),
    ("Who is Ann's husband?", "Brett"),
    ("Who is Carol's father?", "Brett"),
    ("Who is Emily's father?", "Don't know"),
    ("Who is Carol's daughter?", "Emily"),
    ("Who is Frank's brother?", "Darren"),
    ("Who is Darren's brother?", "Frank?"),
    ("Who is Emily's grandfather?", "Brett"),
    ("Who is Ann's granddaughter?", "Emily"),
    ("Who is Frank's father?", "Brett"),
    ("Who is Emily's grandmother?", "Ann"),
    ("Who is Nathan's brother?", "John"),
    ("Who is Jeremy's wife?", "Lily?")])
def test_base(question, answer):
    assert ph.request(question) == answer


@pytest.mark.parametrize("question, answer", [
    ("Who is Brett's son?", {"Darren", "Frank?"}),
    ("Who is Ann's child?", {"Carol", "Darren", "Frank"}),
    ("Who is Darren's sister?", {"Carol", "Frank?"}),
    ("Who is Ann's grandchild?", {"Emily", "Nathan", "John"})])
def test_multiple(question, answer):
    assert set(ph.request(question).split(", ")) == answer
