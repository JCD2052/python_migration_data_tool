import os
from threading import Lock
from typing import Tuple, List

from bs4 import BeautifulSoup
from spellchecker import SpellChecker
from textblob import Word

from category_normalization.validators.base_validator import BaseValidator
from category_normalization.validators.google_search_client import GoogleSearchClient
from utils.string_utils import EMPTY_STRING, ALPHABET_STRING


class SpellCheckValidator(BaseValidator):
    _PRIORITY = 10
    _COLOR = 'orange'
    _NAME = 'Misspelled word'
    __SPELL_CHECKER = SpellChecker()
    __DICT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/words.txt'))
    __SPELL_CHECKER.word_frequency.load_text_file(__DICT_PATH)
    __GOOGLE_SEARCH_CLIENT = GoogleSearchClient()
    __A_TAG = 'a'
    __TAG_ID = 'fprsl'
    __L0CK = Lock()
    __TOO_MANY_REQUESTS_STATUS_CODE = 429

    def validate(self, value: str) -> Tuple[bool, str]:
        errors = self.__check_for_errors_by_spellcheckers(value)
        return bool(errors), f'The value includes the following misspellings: {", ".join(errors)}'

    def __check_for_errors_by_spellcheckers(self, value: str) -> List[str]:
        if not value:
            return []
        res = []
        words = list(filter(lambda x: x.isupper() is False and x.isalpha(), self.__SPELL_CHECKER.split_words(value)))
        for word in words:
            for letter in word:
                    if letter.lower() not in ALPHABET_STRING:
                        res.append(word)
                        return res
            misspells = list(self.__SPELL_CHECKER.unknown([word]))
            if not misspells:
                res = res + misspells
                continue
            else:
                singular = Word(word).singularize().string
                misspells = list(self.__SPELL_CHECKER.unknown([singular]))
                res = res + misspells
        if res:
            google_search_result = self.__check_spelling_in_google_search(value)
            if not google_search_result:
                with self.__L0CK:
                    with open(self.__DICT_PATH, mode='a+') as file:
                        file.seek(0)
                        content = [x.lower() for x in file.read().split(",")]
                        for w in res:
                            if w.lower() not in content:
                                file.write(f"{w},")
                return [] if not google_search_result else [google_search_result]
        return res

    def __check_spelling_in_google_search(self, word: str) -> str:
        response = self.__GOOGLE_SEARCH_CLIENT.get_response(word)
        print(response.status_code)
        if response.status_code == self.__TOO_MANY_REQUESTS_STATUS_CODE:
            return "Status code 429 - Too many requests"
        soup = BeautifulSoup(response.text, "html.parser")
        parent_tag = soup.find(self.__A_TAG, id=self.__TAG_ID)
        return parent_tag.find_next().text if parent_tag is not None else EMPTY_STRING
