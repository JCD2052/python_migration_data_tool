import abc
import itertools
import re
import os
from typing import Set, Tuple, List, Dict

from spellchecker import SpellChecker
from textblob import Word

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
    _PRIORITY = 6
    _COLOR = 'green'
    _NAME = 'Lower \'and\''

    def validate(self, value: str) -> Tuple[bool, str]:
        return ' and ' in value, 'Value contains \'and\' inside '


class SpecialCharactersValidator(BaseValidator):
    _PRIORITY = 8
    _COLOR = 'yellow'
    _NAME = 'Special character'

    def validate(self, value: str) -> Tuple[bool, str]:
        replaced_value = value.replace(SPACE_STRING, '')
        spec_characters = ", ".join(
            [f'"{char}"' for char in set(re.sub("[a-zA-Z0-9]", "", replaced_value))])
        return (not replaced_value.isalnum(),
                f'Value contains special character inside: '
                f'{spec_characters}')


class ExtraSpacesValidator(BaseValidator):
    _PRIORITY = 5
    _COLOR = 'blue'
    _NAME = 'Extra spaces'

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
    _PRIORITY = 3
    _COLOR = 'grey'
    _NAME = 'Almost same category name'

    def __init__(self, values_list: list) -> None:
        self.__duplicate_dict = self.__get_duplicate_values_with_normalization(values_list)
        self.__duplicate_values = BaseValidator.find_duplicates_in_dict(self.__duplicate_dict)

    def validate(self, value: str) -> Tuple[bool, str]:
        return (value in self.__duplicate_values,
                f'Value has almost same category name: '
                f'{" ,".join(self.__duplicate_dict.get(self.__normalize_category(value)))}')

    @staticmethod
    def __get_duplicate_values_with_normalization(values_list: list) -> dict:
        values_list = list(set([value.replace(" and ", " And ").strip() for value in values_list]))
        values = {v: AlmostSameWordValidator.__normalize_category(v) for v in values_list}
        return BaseValidator.build_duplicates_dict(values)

    @staticmethod
    def __normalize_category(category_string: str) -> str:
        sub = re.sub('[^A-Za-z0-9]+', '', category_string.replace('&', 'and').lower())
        return sub


class SpellCheckValidator(BaseValidator):
    _PRIORITY = 7
    _COLOR = 'orange'
    _NAME = 'Misspelled word'
    __spell = SpellChecker()
    __spell.word_frequency.load_text_file(os.path.join(os.path.dirname(__file__), '..\\..\\src\\words.txt'))

    def validate(self, value: str) -> Tuple[bool, str]:
        errors = self.__get_errors_from_word(value)
        return bool(errors), f'Value has next spellchecks errors: {", ".join(errors)}'

    def __get_errors_from_word(self, word: str) -> List[str]:
        if not word:
            return []
        res = []
        words = list(filter(lambda x: x.isupper() is False and x.isalpha(), self.__spell.split_words(word)))
        for word in words:
            misspells = list(self.__spell.unknown([word]))
            if not misspells:
                res = res + misspells
                continue
            else:
                singular = Word(word).singularize().string
                misspells = list(self.__spell.unknown([singular]))
                res = res + misspells
        return res


class DuplicatesInColumnValidator(BaseValidator):
    _PRIORITY = 2
    _COLOR = 'red'
    _NAME = "Duplicate in another column"

    def __init__(self, category_leveling: Dict[str, List[str]]) -> None:
        self.__category_leveling = category_leveling

    def validate(self, value: str) -> Tuple[bool, str]:
        levels = self.__category_leveling.get(value)
        return (len(levels) > 1,
                f'Value duplicated in the next columns {" , ".join(levels)}')


class SkuDuplicateValidator(BaseValidator):
    _PRIORITY = 1
    _COLOR = 'brown'
    _NAME = 'Duplicate in MPSku column'

    def validate(self, value: str) -> Tuple[bool, str]:
        return bool(re.match(r"[A-Za-z]{2}-.*", value)), f'Value \'{value}\' has duplicates in Sku column'
