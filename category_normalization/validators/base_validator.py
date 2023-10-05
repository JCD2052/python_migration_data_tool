import itertools
import re
from abc import ABC, abstractmethod
from typing import Tuple, Set

from utils.string_utils import SPACE_STRING
from category_normalization.data_manipulation.description import description


class BaseValidator(ABC):
    _PRIORITY = int()
    _COLOR = ''
    _NAME = ''
    _DESCRIPTION_DICT = description

    @abstractmethod
    def validate(self, value: str) -> Tuple[bool, str]:
        pass

    @classmethod
    def get_priority(cls) -> int:
        return cls._PRIORITY

    @classmethod
    def get_name(cls) -> str:
        return cls._NAME

    @classmethod
    def get_description(cls) -> str:
        return cls._DESCRIPTION_DICT[cls._NAME]

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

    @staticmethod
    def normalize_category(category_string: str) -> str:
        sub = re.sub('[^A-Za-z0-9]+', '', category_string.replace('&', 'and').lower())
        return sub


class LowerAndValidator(BaseValidator):
    _PRIORITY = 9
    _COLOR = 'green'
    _NAME = "Lower 'and'"

    def validate(self, value: str) -> Tuple[bool, str]:
        return ' and ' in value, 'The value contains \'and\''


class SpecialCharactersValidator(BaseValidator):
    _PRIORITY = 11
    _COLOR = 'lightgrey'
    _NAME = 'Special character'

    def validate(self, value: str) -> Tuple[bool, str]:
        replaced_value = value.replace(SPACE_STRING, '').replace(',', '')
        spec_characters = ", ".join(
            [f'"{char}"' for char in set(re.sub("[a-zA-Z0-9]", "", replaced_value))])
        return (not replaced_value.isalnum(),
                f'The value contains special character inside: '
                f'{spec_characters}')


class ExtraSpacesValidator(BaseValidator):
    _PRIORITY = 7
    _COLOR = 'lightgreen'
    _NAME = 'Extra space'

    def validate(self, value: str) -> Tuple[bool, str]:
        return (value.startswith(SPACE_STRING) or value.endswith(
            SPACE_STRING) or f'{SPACE_STRING}{SPACE_STRING}' in value,
                f'The value contains an extra space')


class NonBreakingSpaceValidator(BaseValidator):
    _PRIORITY = 6
    _COLOR = 'lightblue'
    _NAME = 'Non-breaking space'

    def validate(self, value: str) -> Tuple[bool, str]:
        return u"\u00A0" in value, f'The value contains a non-breaking space'


class UpperMPInSkuValidator(BaseValidator):
    _PRIORITY = 3
    _COLOR = 'pink'
    _NAME = "Upper 'MP-' in MPSku column"

    def validate(self, value: str) -> Tuple[bool, str]:
        if value.lower().startswith("mp-"):
            return not bool(re.match(r"mp-.*", value)), f'The value contains uppercase char'
        else:
            return False, f"The value doesn't start with 'mp-'"
