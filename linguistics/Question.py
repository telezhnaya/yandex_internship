# -*- coding: utf-8 -*-
import pytest

from collections import deque

# Несколько условностей, которые я приняла как правило:
# Все предложения на входе всегда даны в верхнем регистре и без точки в конце.
# В случае сложносоставного глагола * ставится после первого
# (того, который уйдет в начало).
# Добавила символ: решетка в предложении как показатель отсутствия модальности.
# В случае использования have to или устойчивых словосочетаний (to have dinner,
# to have a walk) нужно поставить # в любое место в предложении.
# Можно также поставить # в любом предложении с have,
# где мы бы не хотели использовать have как модальный глагол.
# Я не стала даже пытаться поддерживать Past Simple, потому что
# для его поддержки необходимо учитывать неправильные глаголы. Для этого
# нужно подключать сторонние библиотеки (так как вручную не перечислить).
# В таком случае, можно было решить всю проблему с помощью сторонних библиотек.
# Но, как я поняла, суть задания была не в этом. Надеюсь, наши мнения сойдутся.


class Questioner(object):
    @staticmethod
    def is_aux_or_modal_verb(word):
        return word in ["AM", "IS", "ARE", "DO", "DOES", "MUST", "OUGHT",
                        "CAN", "COULD", "SHALL", "SHOULD", "MAY", "MIGHT",
                        "WILL", "WOULD", "HAVE", "HAS", "WAS", "WERE"]

    @staticmethod
    def calc_negative_particle(verb):
        if verb.endswith("N'T*") or verb.endswith("NOT*"):
            return verb[-4:-1]
        return ""

    @staticmethod
    def has_es_ending(word):
        return word[-3] in "AEIOUYXZ" or word[-4:-2] in ["SS", "SH", "CH"]

    def get_question_word(self, word, not_modal):
        if not_modal or not self.is_aux_or_modal_verb(word):
            ans = "DOES" if word != self.get_verb_lemma(word) else "DO"
        else:
            ans = word
        return ans + self.negative_particle

    def get_verb_lemma(self, word):
        if word == "HAS":
            return "HAVE"
        if word.endswith("ES") and self.has_es_ending(word):
            return word[:-2] if word[-3] != "I" else word[:-3] + "Y"
        if word.endswith("S") and not word.endswith("SS"):
            return word[:-1]
        return word

    def prepare(self, statement):
        statement = statement.replace("#", "")
        words = statement.split()
        pos = next(i for i, w in enumerate(words) if w.endswith("*"))
        verb = words[pos]

        # Отрицательная частица стоит на одном и том же месте. Запомнили, какую
        # предпочел пользователь, убираем ее, потом дописываем к вопр.слову
        self.negative_particle = self.calc_negative_particle(verb)
        words[pos] = verb[:-4] + "*" if self.negative_particle else verb
        if len(words) > pos + 2 and words[pos + 1] == "NOT":
            self.negative_particle = " NOT"
            words.pop(pos + 1)
        return words

    def request(self, statement):
        request = deque()
        surely_not_modal = "#" in statement
        # He plays* and shouts* -> вопр.слово нам нужно лишь одно
        first_verb = True

        for word in self.prepare(statement):
            if word.endswith("*"):
                word = word[:-1]
                if first_verb:
                    q_word = self.get_question_word(word, surely_not_modal)
                    request.appendleft(q_word)
                if surely_not_modal or not self.is_aux_or_modal_verb(word):
                    request.append(self.get_verb_lemma(word))
                first_verb = False
            else:
                request.append(word)
        return " ".join(request) + "?"


q = Questioner()


@pytest.mark.parametrize("question, answer", [
    ("KATE GOES* TO SCHOOL", "DOES KATE GO TO SCHOOL?"),
    ("ALEX IS* TALL", "IS ALEX TALL?"),
    ("WINTER USUALLY COMES* LATE", "DOES WINTER USUALLY COME LATE?"),
    ("STUDENTS OFTEN COME* LATE", "DO STUDENTS OFTEN COME LATE?"),
    ("I HAVE* A CAR#", "DO I HAVE A CAR?"),
    ("I HAVE* A CAR", "HAVE I A CAR?"),
    ("LIBRARY ... POSSESSES* BOOKS", "DOES LIBRARY ... POSSESS BOOKS?"),
    ("I MISS* MY DOG", "DO I MISS MY DOG?"),
    ("THEY FIX* EVERYTHING", "DO THEY FIX EVERYTHING?"),
    ("HE MUST* DO HIS HOMEWORK", "MUST HE DO HIS HOMEWORK?"),
    ("I CAN* HELP YOU", "CAN I HELP YOU?"),
    ("KATE STUDIES* WELL", "DOES KATE STUDY WELL?"),
    ("THEY HAVE* BEEN WORKING ALL NIGHT", "HAVE THEY BEEN WORKING ALL NIGHT?"),
    ("KATE WILL* STUDY WELL", "WILL KATE STUDY WELL?"),
    ("HE WAS* ASKED ABOUT IT", "WAS HE ASKED ABOUT IT?"),
    ("HE HAS* TO# GO THERE", "DOES HE HAVE TO GO THERE?"),
    ("I HAVE* TO# GO THERE", "DO I HAVE TO GO THERE?"),
    ("HE NEEDS* TO GO THERE", "DOES HE NEED TO GO THERE?"),
    ("I HAVE* A WALK#", "DO I HAVE A WALK?"),
    ("HE HAS* A CAR#", "DOES HE HAVE A CAR?"),
    ("HE OFTEN HAS* TO# GET UP EARLY", "DOES HE OFTEN HAVE TO GET UP EARLY?"),
    ("HE DOES* HIS HOMEWORK#", "DOES HE DO HIS HOMEWORK?"),
    ("HE HASN'T* SPENT ALL THE TIME", "HASN'T HE SPENT ALL THE TIME?"),
    ("I HAVEN'T* SPENT ALL THE TIME", "HAVEN'T I SPENT ALL THE TIME?"),
    ("I DON'T* GO TO SCHOOL", "DON'T I GO TO SCHOOL?"),
    ("KATE DOESN'T* GO TO SCHOOL", "DOESN'T KATE GO TO SCHOOL?"),
    ("HE HASN'T* TO# GO THERE", "DOESN'T HE HAVE TO GO THERE?"),
    ("I HAVEN'T* TO# GO THERE", "DON'T I HAVE TO GO THERE?"),
    ("HE HAS* NOT SPENT ALL THE TIME", "HAS NOT HE SPENT ALL THE TIME?"),
    ("I HAVE* NOT SPENT ALL THE TIME", "HAVE NOT I SPENT ALL THE TIME?"),
    ("I DO* NOT GO TO SCHOOL", "DO NOT I GO TO SCHOOL?"),
    ("KATE DOES* NOT GO TO SCHOOL", "DOES NOT KATE GO TO SCHOOL?"),
    ("HE HAS* NOT TO# GO THERE", "DOES NOT HE HAVE TO GO THERE?"),
    ("I HAVE* NOT TO# GO THERE", "DO NOT I HAVE TO GO THERE?"),
    ("I DO* MY FAVOUR#", "DO I DO MY FAVOUR?"),
    ("HE DOES* MAKE SMTH", "DOES HE MAKE SMTH?"),
    ("HE GOES* AND MAKES* SMTH", "DOES HE GO AND MAKE SMTH?")])
def test_base(question, answer):
    assert q.request(question) == answer
