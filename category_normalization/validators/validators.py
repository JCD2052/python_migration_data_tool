import abc
from typing import Set

from spellchecker import SpellChecker
from textblob import Word

SPACE_STRING = ' '
spell = SpellChecker()
spell.word_frequency.load_text_file(
    'C:\\Users\\proje\\PycharmProjects\\python_migration_data_tool\\category_normalization\\words.txt')


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


class LowerAndValidator(BaseValidator):
    _PRIORITY = 1
    _COLOR = 'green'

    def validate(self, value: str) -> bool:
        return ' and ' in value


class SpecialCharactersValidator(BaseValidator):
    _PRIORITY = 2
    _COLOR = 'yellow'

    def validate(self, value: str) -> bool:
        return not value.isalnum()


class ExtraSpacesValidator(BaseValidator):
    _PRIORITY = 3
    _COLOR = 'blue'

    def validate(self, value: str) -> bool:
        return value.startswith(SPACE_STRING) or value.endswith(SPACE_STRING)


class ExtraSpacesBetweenWordsValidator(BaseValidator):
    _PRIORITY = 4
    _COLOR = 'brown'

    def validate(self, value: str) -> bool:
        return bool(list(
            filter(lambda x: x.endswith(SPACE_STRING) or x.startswith(SPACE_STRING), value.split(SPACE_STRING))))


class AlmostSameWordValidator(BaseValidator):
    _PRIORITY = 5
    _COLOR = 'darkblue'

    def __init__(self, values: Set[str]):
        self.__values = values

    def validate(self, value: str) -> bool:
        return value in self.__values


class SpellCheckValidator(BaseValidator):
    _PRIORITY = 6
    _COLOR = 'orange'

    def validate(self, value: str) -> bool:
        return self.__is_word_with_errors(value)

    @staticmethod
    def __is_word_with_errors(word: str) -> bool:
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
