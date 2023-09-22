import abc
import itertools
import os
import re
from typing import Set, Tuple, List, Dict

from spellchecker import SpellChecker
from textblob import Word

from utils.string_utils import EMPTY_STRING
from threading import Lock
from bs4 import BeautifulSoup

from category_normalization.validators.google_search_client import GoogleSearchClient

SPACE_STRING = ' '


class BaseValidator(abc.ABC):
    _PRIORITY = int()
    _COLOR = ''
    _NAME = ''

    @abc.abstractmethod
    def validate(self, value: str) -> Tuple[bool, str]:
        pass

    @classmethod
    def get_priority(cls) -> int:
        return cls._PRIORITY

    @classmethod
    def get_name(cls) -> str:
        return cls._NAME

    @classmethod
    def get_background_color(cls) -> str:
        return f'background-color: {cls._COLOR}'

    @staticmethod
    def build_duplicates_dict(origin_dict: dict) -> dict:
        rev_dict = {}
        for k, v in origin_dict.items():
            rev_dict.setdefault(v, set()).add(k)

        return rev_dict

    @staticmethod
    def find_duplicates_in_dict(origin_dict: dict) -> Set[str]:
        return set(itertools.chain.from_iterable(
            values for key, values in origin_dict.items()
            if len(values) > 1))


class LowerAndValidator(BaseValidator):
    _PRIORITY = 7
    _COLOR = 'green'
    _NAME = 'Lower \'and\''

    def validate(self, value: str) -> Tuple[bool, str]:
        return ' and ' in value, 'Value contains \'and\' inside '


class SpecialCharactersValidator(BaseValidator):
    _PRIORITY = 9
    _COLOR = 'grey'
    _NAME = 'Special character'

    def validate(self, value: str) -> Tuple[bool, str]:
        replaced_value = value.replace(SPACE_STRING, '').replace(',', '')
        spec_characters = ", ".join(
            [f'"{char}"' for char in set(re.sub("[a-zA-Z0-9]", "", replaced_value))])
        return (not replaced_value.isalnum(),
                f'Value contains special character inside: '
                f'{spec_characters}')


class ExtraSpacesValidator(BaseValidator):
    _PRIORITY = 5
    _COLOR = 'lightgreen'
    _NAME = 'Extra space'

    def validate(self, value: str) -> Tuple[bool, str]:
        return (value.startswith(SPACE_STRING) or value.endswith(
            SPACE_STRING) or f'{SPACE_STRING}{SPACE_STRING}' in value,
                f'Value contains spaces in start or end')


class NonBreakingSpaceValidator(BaseValidator):
    _PRIORITY = 4
    _COLOR = 'lightblue'
    _NAME = 'Non-breaking space'

    def validate(self, value: str) -> Tuple[bool, str]:
        return u"\u00A0" in value, f'Value has non-breaking space inside.'


class AlmostSameWordValidator(BaseValidator):
    _PRIORITY = 6
    _COLOR = 'yellow'
    _NAME = 'Almost same category name'

    def __init__(self, values_list: list) -> None:
        self.__duplicate_dict = self.__get_duplicate_values_with_normalization(values_list)
        self.__duplicate_values = BaseValidator.find_duplicates_in_dict(self.__duplicate_dict)

    def validate(self, value: str) -> Tuple[bool, str]:
        return (value in self.__duplicate_values,
                f'Value has almost same category name: '
                f'({"), (".join(self.__duplicate_dict.get(self.__normalize_category(value)))})')

    @staticmethod
    def __get_duplicate_values_with_normalization(values_list: list) -> dict:
        values_list = list(set([value.replace(" and ", " And ") for value in values_list]))
        values = {v: AlmostSameWordValidator.__normalize_category(v) for v in values_list}
        return BaseValidator.build_duplicates_dict(values)

    @staticmethod
    def __normalize_category(category_string: str) -> str:
        sub = re.sub('[^A-Za-z0-9]+', '', category_string.replace('&', 'and').lower())
        return sub


class SpellCheckValidator(BaseValidator):
    _PRIORITY = 8
    _COLOR = 'orange'
    _NAME = 'Misspelled word'
    __SPELL_CHECKER = SpellChecker()
    __DICT_PATH = os.path.join(os.path.dirname(__file__), '..\\..\\src\\words.txt')
    __SPELL_CHECKER.word_frequency.load_text_file(__DICT_PATH)
    __GOOGLE_SEARCH_CLIENT = GoogleSearchClient()
    __A_TAG = 'a'
    __TAG_ID = 'fprsl'
    __L0CK = Lock()
    __TOO_MANY_REQUESTS_STATUS_CODE = 429

    def validate(self, value: str) -> Tuple[bool, str]:
        errors = self.__check_for_errors_by_spellcheckers(value)
        return bool(errors), f'Value has next spellchecks errors: {", ".join(errors)}'

    def __check_for_errors_by_spellcheckers(self, value: str) -> List[str]:
        if not value:
            return []
        res = []
        words = list(filter(lambda x: x.isupper() is False and x.isalpha(), self.__SPELL_CHECKER.split_words(value)))
        for word in words:
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


class DuplicatesInColumnValidator(BaseValidator):
    _PRIORITY = 2
    _COLOR = 'red'
    _NAME = "Duplicate in category value"

    def __init__(self, category_leveling: Dict[str, List[str]]) -> None:
        self.__category_leveling = category_leveling

    def validate(self, value: str) -> Tuple[bool, str]:
        levels = self.__category_leveling.get(value)
        return (len(levels) > 1,
                f'Value duplicated in the next columns {" , ".join(levels)}')


class DuplicateInSkuValidator(BaseValidator):
    _PRIORITY = 1
    _COLOR = 'brown'
    _NAME = 'Duplicate in MPSku column'

    def __init__(self, duplicates_list: list) -> None:
        self.duplucates_list = [value.lower() for value in duplicates_list]

    def validate(self, value: str) -> Tuple[bool, str]:
        return (bool(re.match(r"[A-Za-z]{2}-.*", value)) and (value.lower() in self.duplucates_list),
                f'Value has duplicates in Sku column')


class UpperMPInSkuValidator(BaseValidator):
    _PRIORITY = 3
    _COLOR = 'pink'
    _NAME = 'Upper \'MP-\' in MPSku column'

    def validate(self, value: str) -> Tuple[bool, str]:
        if value.lower().startswith("mp-"):
            return not bool(re.match(r"mp-.*", value)), f'Value contains uppercase char'
        else:
            return False, f'Value  doesn\'t start with "mp-"'
