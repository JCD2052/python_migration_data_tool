import abc
import itertools
import re
from typing import Set

from spellchecker import SpellChecker
from textblob import Word

SPACE_STRING = ' '


class BaseValidator(abc.ABC):
    _PRIORITY = int()
    _COLOR = ''

    @abc.abstractmethod
    def validate(self, value: str) -> bool:
        pass

    @classmethod
    def get_priority(cls) -> int:
        return cls._PRIORITY

    @classmethod
    def get_background_color(cls) -> str:
        return f'background-color: {cls._COLOR}'

    @staticmethod
    def find_duplicates_in_dict(origin_dict: dict) -> Set[str]:
        rev_dict = {}
        for k, v in origin_dict.items():
            rev_dict.setdefault(v, set()).add(k)

        return set(itertools.chain.from_iterable(
            values for key, values in rev_dict.items()
            if len(values) > 1))


class LowerAndValidator(BaseValidator):
    _PRIORITY = 1
    _COLOR = 'green'

    def validate(self, value: str) -> bool:
        return ' and ' in value


class SpecialCharactersValidator(BaseValidator):
    _PRIORITY = 2
    _COLOR = 'yellow'

    def validate(self, value: str) -> bool:
        return not value.replace(SPACE_STRING, '').isalnum()


class ExtraSpacesValidator(BaseValidator):
    _PRIORITY = 3
    _COLOR = 'blue'

    def validate(self, value: str) -> bool:
        return value.startswith(SPACE_STRING) or value.endswith(
            SPACE_STRING) or f'{SPACE_STRING}{SPACE_STRING}' in value


class NonBreakingSpaceValidator(BaseValidator):
    _PRIORITY = 0
    _COLOR = 'lightgreen'

    def validate(self, value: str) -> bool:
        return u"\u00A0" in value


class AlmostSameWordValidator(BaseValidator):
    _PRIORITY = 5
    _COLOR = 'darkblue'

    def __init__(self, values_list: list) -> None:
        self.__values = values_list

    def validate(self, value: str) -> bool:
        return value in self.__get_duplicate_values_with_normalization(self.__values)

    @staticmethod
    def __get_duplicate_values_with_normalization(values_list: list) -> Set[str]:
        values = {v: AlmostSameWordValidator.__normalize_category(v) for v in values_list}
        return BaseValidator.find_duplicates_in_dict(values)

    @staticmethod
    def __normalize_category(category_string: str) -> str:
        sub = re.sub('[^A-Za-z0-9]+', '', category_string.replace('&', 'and').lower())
        return sub


class SpellCheckValidator(BaseValidator):
    _PRIORITY = 6
    _COLOR = 'orange'
    _spell = SpellChecker()
    _spell.word_frequency.load_text_file('src\\words.txt')

    def validate(self, value: str) -> bool:
        return self.__is_word_with_errors(value, self._spell)

    @staticmethod
    def __is_word_with_errors(word: str, spell) -> bool:
        if not word:
            return False
        res = []
        words = list(filter(lambda x: x.isupper() is False and x.isalpha(), spell.split_words(word)))
        print(f'words after split: {words}')
        for word in words:
            misspells = list(spell.unknown([word]))
            print(f'init misspells {misspells}')
            if not misspells:
                res = res + misspells
                continue
            else:
                singular = Word(word).singularize().string
                print(f'singular version of {word}: - {singular}')
                misspells = list(spell.unknown([singular]))
                print(f'misspells after singular {misspells}')
                res = res + misspells
        print(f'final result {res}')
        return bool(res)


class DuplicatesInColumnValidator(BaseValidator):
    _PRIORITY = 7
    _COLOR = 'lightyellow'

    def __init__(self, categories_dict: dict) -> None:
        self.__categories_dict = categories_dict

    def validate(self, value: str) -> bool:
        return value in BaseValidator.find_duplicates_in_dict(self.__categories_dict)


class SkuDuplicateValidator(BaseValidator):
    _PRIORITY = 8
    _COLOR = 'brown'

    def validate(self, value: str) -> bool:
        return bool(re.match(r"[A-Za-z]{2}-.*", value))
