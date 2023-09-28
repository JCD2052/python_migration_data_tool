import multiprocessing
from asyncio import Future
from concurrent.futures import ThreadPoolExecutor
from multiprocessing.pool import ThreadPool
from typing import Tuple, Dict, List, Set

from pandas import DataFrame

from category_normalization.validators.base_validator import BaseValidator


class DuplicateWithWrongHierarchyValidator(BaseValidator):
    _PRIORITY = 5
    _COLOR = 'coral'
    _NAME = 'Duplicates with wrong hierarchy'

    def __init__(self, data: DataFrame = DataFrame()) -> None:
        self.__data: DataFrame = data
        self.__data_dict: Dict[str, str] = self.__find_categories_with_wrong_hierarchy()

    def validate(self, value: str) -> Tuple[bool, str]:
        result: str = self.__data_dict.get(value)
        return bool(result), result

    def __find_categories_with_wrong_hierarchy(self) -> Dict[str, str]:
        num_processes: int = multiprocessing.cpu_count()
        chunk_size: int = int(self.__data.shape[0] / num_processes)
        chunks: List[DataFrame] = [self.__data.iloc[self.__data.index[i:i + chunk_size]] for i in
                                   range(0, self.__data.shape[0], chunk_size)]
        with ThreadPool(num_processes) as pool:
            data: List[Dict[str, str]] = pool.map(self.__check_frame_chunk, chunks)
            return {k: v for d in data for k, v in d.items()}

    def __check_frame_chunk(self, chunk_frame: DataFrame) -> Dict[str, str]:
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures: List[Future] = [executor.submit(self.__check_row, row) for row
                                     in
                                     chunk_frame.iterrows()]
            return {k: v for call in futures for k, v in call.result().items()}

    def __check_row(self, row) -> Dict[str, str]:
        columns: List[str] = self.__data.columns
        filtered_row: List[str] = [v for v in list(row[1][columns].values) if bool(v)]
        value: str = filtered_row[-1]
        value_column: str = columns[filtered_row.index(value)]
        duplicated_values: DataFrame = self.__data.loc[self.__data[value_column] == value][columns]
        if not len(duplicated_values) <= 1:
            values: Set[Tuple[str]] = set([tuple(v[0:filtered_row.index(value)]) for v in duplicated_values.values])
            if len(values) > 1:
                return {value: f"wrong category hierarchies for value {value}: "
                               f"{' and '.join(list(map(lambda x: '(' + '-->'.join(x) + ')', values)))}"}
            else:
                return {value: f'category {value} in column {value_column} is completely duplicated.'}
        else:
            return {}
