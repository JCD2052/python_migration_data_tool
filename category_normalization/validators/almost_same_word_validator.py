import itertools
from typing import Tuple, List, Dict

from pandas import DataFrame

from category_normalization.validators.base_validator import BaseValidator


class AlmostSameWordValidator(BaseValidator):
    _PRIORITY = 8
    _COLOR = 'yellow'
    _NAME = 'Almost same category name'

    def __init__(self, data: DataFrame) -> None:
        self.__duplicate_dict = self.__get_duplicate_values_with_normalization(
            self.__get_unique_values_from_table(data))
        self.__duplicate_values = BaseValidator.find_duplicates_in_dict(self.__duplicate_dict)

    def validate(self, value: str) -> Tuple[bool, str]:
        return (value in self.__duplicate_values,
                f'The value has almost same category name: '
                f'({"), (".join(self.__duplicate_dict.get(self.normalize_category(value), []))})')

    @staticmethod
    def __get_unique_values_from_table(data: DataFrame) -> List[str]:
        return list(itertools.chain(*[list(filter(lambda value: bool(value), data[column].unique()))
                                      for column in data.columns]))

    @staticmethod
    def __get_duplicate_values_with_normalization(values_list: List[str]) -> Dict[str, str]:
        values_list = list(set([value.replace(" and ", " And ") for value in values_list]))
        values = {v: BaseValidator.normalize_category(v) for v in values_list}
        return BaseValidator.build_duplicates_dict(values)
