import re
from typing import Tuple

from pandas import Series

from category_normalization.validators.base_validator import BaseValidator


class DuplicateInSkuValidator(BaseValidator):
    _PRIORITY = 1
    _COLOR = 'brown'
    _NAME = 'Duplicate in MPSku column'

    def __init__(self, data: Series = Series()) -> None:
        self.duplicates_list = self.__find_duplicates_in_sku_column(data)

    def validate(self, value: str) -> Tuple[bool, str]:
        return (bool(re.match(r"[A-Za-z]{2}-.*", value)) and (value.lower() in self.duplicates_list),
                f'The value is duplicated in the MPSku column')

    @staticmethod
    def __find_duplicates_in_sku_column(data: Series):
        return list(data[data.duplicated() == True])
