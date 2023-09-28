from asyncio import Future
from concurrent.futures import ThreadPoolExecutor
from typing import Tuple, List, Iterable

from pandas import DataFrame, Series

from category_normalization.validators.base_validator import BaseValidator
from utils.string_utils import EMPTY_STRING


class CheckCategoryHierarchyValidator(BaseValidator):
    _PRIORITY = 4
    _COLOR = 'olive'
    _NAME = 'Category Hierarchy Errors'

    def __init__(self, data: DataFrame = DataFrame()) -> None:
        self.__data = data
        self.__values = self.find_duplicated_categories_with_wrong_leveling()

    def validate(self, value: str) -> Tuple[bool, str]:
        return value in self.__values, f'The value {value} has the wrong hierarchy'

    def find_duplicated_categories_with_wrong_leveling(self) -> List[str]:
        res: List[str] = []
        category_columns = list(self.__data.columns)
        for column in category_columns:
            current_column_index: int = category_columns.index(column)
            columns_before: List[str] = category_columns[0:current_column_index]
            if not columns_before:
                continue
            duplicated_value: Iterable[str] = filter(lambda value: bool(value),
                                                     set(self.__data[self.__data[column].duplicated() == True][column]))

            with ThreadPoolExecutor(max_workers=8) as executor:
                futures: List[Future] = [executor.submit(self.__validate_value, value, column, columns_before) for value
                                         in
                                         duplicated_value]
                future_results: List[str] = list(filter(lambda res_from_future: bool(res_from_future),
                                                        [call.result() for call in futures]))
                res = res + future_results
        return res

    def __validate_value(self, value: str, column: str, columns_range: List[str]) -> str:
        res: Series = self.__data.loc[self.__data[column] == value][columns_range]
        normalized_values_func = lambda data_array: [self.normalize_category(i) for i in data_array]
        first_value = normalized_values_func(res.values[0])
        results: bool = all([normalized_values_func(row) == first_value for row in res.values])
        if not results:
            return value
        else:
            return EMPTY_STRING
