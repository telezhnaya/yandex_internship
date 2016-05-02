# -*- coding: utf-8 -*-

from collections import deque


class Questioner(object):
    @staticmethod
    def is_aux_or_modal_verb(word):
        return word in "AM IS ARE MUST OUGHT CAN COULD SHALL SHOULD " \
                               "MAY MIGHT WILL WOULD HAVE HAS WAS WERE".split()

    def cut_negative(self, word):
        is_negative = word.endswith("N'T") or word.endswith("NOT")
        self.negative_particle = word[-3:] if is_negative else ""
        return word[:-3] if is_negative else word

    def get_question_word(self, word, not_modal):
        if not_modal or not self.is_aux_or_modal_verb(word):
            ans = "DOES" if word != self.get_verb_lemma(word) else "DO"
        else:
            ans = word
        return ans + self.negative_particle

    @staticmethod
    def has_es_ending(word):
        return word[-3] in "AEIOUXZ" or word[-4:-2] in "SS SH CH".split()

    def get_verb_lemma(self, word):
        if word == "HAS":
            return "HAVE"
        if word.endswith("ES") and self.has_es_ending(word):
            if word[-3] == "I":
                return word[:-3] + "Y"
            return word[:-2]
        elif word.endswith("S") and not word.endswith("SS"):
            return word[:-1]
        else:
            return word

    def request(self, statement):
        request = deque()
        for word in statement.strip().split():
            if word.endswith("*"):
                word = word[:-1]
                word = self.cut_negative(word)
                surely_not_modal = statement.find("#") != -1
                request.appendleft(self.get_question_word(word, surely_not_modal))
                if surely_not_modal or not self.is_aux_or_modal_verb(word):
                    word = self.get_verb_lemma(word)
                    if word != "DO" or not self.negative_particle:
                        request.append(word)
            else:
                request.append(word.replace("#", ""))
        return " ".join(request) + "?"

if __name__ == "__main__":
    q = Questioner()
    assert q.request("KATE GOES* TO SCHOOL") == "DOES KATE GO TO SCHOOL?"
    assert q.request("ALEX IS* TALL") == "IS ALEX TALL?"
    assert q.request("WINTER USUALLY COMES* LATE") == "DOES WINTER USUALLY COME LATE?"
    assert q.request("STUDENTS OFTEN COME* LATE") == "DO STUDENTS OFTEN COME LATE?"
    # Оба варианта позволительны, но использование have в качестве модального
    # позволит обобщить код (для использования в других временах, к примеру)
    assert q.request("I HAVE* A CAR") == "HAVE I A CAR?"
    assert q.request("LIBRARY OF CONGRESS POSSESSES* BOOKS") == "DOES LIBRARY OF CONGRESS POSSESS BOOKS?"
    assert q.request("I MISS* MY DOG") == "DO I MISS MY DOG?"
    assert q.request("THEY FIX* EVERYTHING") == "DO THEY FIX EVERYTHING?"
    assert q.request("HE MUST* DO HIS HOMEWORK") == "MUST HE DO HIS HOMEWORK?"
    assert q.request("I CAN* HELP YOU") == "CAN I HELP YOU?"
    assert q.request("KATE STUDIES* WELL") == "DOES KATE STUDY WELL?"
    assert q.request("THEY HAVE* BEEN WORKING ALL NIGHT") == "HAVE THEY BEEN WORKING ALL NIGHT?"
    assert q.request("KATE WILL* STUDY WELL") == "WILL KATE STUDY WELL?"
    assert q.request("HE WAS* ASKED ABOUT IT") == "WAS HE ASKED ABOUT IT?"
    assert q.request("HE HAS* TO# GO THERE") == "DOES HE HAVE TO GO THERE?"
    assert q.request("I HAVE* TO# GO THERE") == "DO I HAVE TO GO THERE?"
    assert q.request("HE NEEDS* TO GO THERE") == "DOES HE NEED TO GO THERE?"
    assert q.request("I HAVE* A WALK#") == "DO I HAVE A WALK?"
    assert q.request("HE HAS* A CAR#") == "DOES HE HAVE A CAR?"
    assert q.request("HE OFTEN HAS* TO# GET UP EARLY") == "DOES HE OFTEN HAVE TO GET UP EARLY?"
    assert q.request("HE DOES* HIS HOMEWORK") == "DOES HE DO HIS HOMEWORK?"
    assert q.request("HE HASN'T* SPENT ALL THE TIME") == "HASN'T HE SPENT ALL THE TIME?"
    assert q.request("I HAVEN'T* SPENT ALL THE TIME") == "HAVEN'T I SPENT ALL THE TIME?"
    assert q.request("I DON'T* GO TO SCHOOL") == "DON'T I GO TO SCHOOL?"
    assert q.request("KATE DOESN'T* GO TO SCHOOL") == "DOESN'T KATE GO TO SCHOOL?"
    assert q.request("HE HASN'T* TO# GO THERE") == "DOESN'T HE HAVE TO GO THERE?"
    assert q.request("I HAVEN'T* TO# GO THERE") == "DON'T I HAVE TO GO THERE?"
