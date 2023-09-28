from typing import Tuple, Dict, List

from pandas import DataFrame

from category_normalization.validators.base_validator import BaseValidator


class DuplicatesInColumnValidator(BaseValidator):
    _PRIORITY = 2
    _COLOR = 'red'
    _NAME = "Duplicate in category value"

    def __init__(self, data: DataFrame = DataFrame()) -> None:
        self.__data = data
        self.__category_leveling = self.get_column_almost_same_values()

    def validate(self, value: str) -> Tuple[bool, str]:
        levels = self.__category_leveling.get(value, [])
        return (len(levels) > 1,
                f'The value is duplicated in the following columns {" , ".join(levels)}')

    def get_column_almost_same_values(self) -> Dict[str, List[str]]:
        column_values: Dict[str, List[str]] = dict()
        for col in self.__data.columns:
            for v in filter(lambda x: bool(x), self.__data[col].unique()):
                if v not in column_values:
                    column_values.update({v: [col]})
                else:
                    column_values[v] = column_values[v] + [col]
        return column_values
