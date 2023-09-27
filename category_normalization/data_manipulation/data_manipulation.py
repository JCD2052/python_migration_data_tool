import itertools
import re
from concurrent.futures import ThreadPoolExecutor, Future
from typing import List, Dict, Set, Tuple, Iterable

import multiprocessing

import pandas as pd


class DataManipulation:
    __CATEGORY_COLUMN_PREFIX: str = 'l'

    def __init__(self, data_frame: pd.DataFrame) -> None:
        self.__data_frame: pd.DataFrame = data_frame
        self.category_columns: List[str] = list(
            filter(lambda column: str(column).lower().startswith(self.__CATEGORY_COLUMN_PREFIX),
                   self.__data_frame.columns))

    def get_column_almost_same_values(self) -> Dict[str, List[str]]:
        column_values: Dict[str, List[str]] = dict()
        for col in self.category_columns:
            for v in filter(lambda x: bool(x), self.__data_frame[col].unique()):
                if v not in column_values:
                    column_values.update({v: [col]})
                else:
                    column_values[v] = column_values[v] + [col]
        return column_values

    def get_unique_values_from_table(self) -> List[str]:
        return list(itertools.chain(*[list(filter(lambda value: bool(value), self.__data_frame[column].unique()))
                                      for column in self.category_columns]))

    def build_values_map(self) -> Dict[str, List[str]]:
        res: Dict[str, List[str]] = dict()
        for column in self.category_columns:
            for v in filter(lambda x: bool(x), self.__data_frame[column].unique()):
                if v not in res:
                    res.update({v: [column]})
                else:
                    res[v] = res[v] + [column]
        return res

    def find_duplicated_categories_with_wrong_leveling(self) -> List[str]:
        res: List[str] = []
        for column in self.category_columns:
            current_column_index: int = self.category_columns.index(column)
            columns_before: List[str] = self.category_columns[0:current_column_index]
            if not columns_before:
                continue
            duplicated_value: Iterable[str] = filter(lambda value: bool(value),
                                                     set(self.__data_frame[
                                                             self.__data_frame[column].duplicated() == True][
                                                             column]))

            with ThreadPoolExecutor(max_workers=8) as executor:
                futures: List[Future] = [executor.submit(self.__validate_value, value, column, columns_before) for value
                                         in
                                         duplicated_value]
                future_results: List[str] = list(filter(lambda res_from_future: res_from_future is not None,
                                                        [call.result() for call in futures]))
                res = res + future_results
        return res

    def find_categories_with_wrong_hierarchy(self) -> Dict[str, str]:
        num_processes = multiprocessing.cpu_count()
        chunk_size = int(self.__data_frame.shape[0] / num_processes)
        chunks = [self.__data_frame.iloc[self.__data_frame.index[i:i + chunk_size]] for i in
                  range(0, self.__data_frame.shape[0], chunk_size)]
        pool = multiprocessing.Pool(processes=num_processes)

        data = pool.map(self.check_frame_chunk, chunks)
        return {k: v for d in data for k, v in d.items()}

    def check_frame_chunk(self, chunk_frame: pd.DataFrame) -> Dict[str, str]:
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures: List[Future] = [executor.submit(self.check_row, row) for row
                                     in
                                     chunk_frame.iterrows()]
            return {k: v for call in futures for k, v in call.result().items()}

    def check_row(self, row) -> Dict[str, str]:
        print(row)
        filtered_row: List[str] = [v for v in list(row[1][self.category_columns].values) if bool(v)]
        value: str = filtered_row[-1]
        value_column: str = self.category_columns[filtered_row.index(value)]
        duplicated_values: pd.DataFrame = self.__data_frame.loc[self.__data_frame[value_column] == value][
            self.category_columns]
        if not len(duplicated_values) <= 1:
            values: Set[Tuple[str]] = set([tuple(v[0:filtered_row.index(value)]) for v in duplicated_values.values])
            if len(values) > 1:
                return {value: f"wrong category hierarchies for value {value}: "
                               f"{' and '.join(list(map(lambda x: '(' + '-->'.join(x) + ')', values)))}"}
            else:
                return {value: f'category {value} in column {value_column} is completely duplicated.'}
        else:
            return {}

    def __validate_value(self, value: str, column: str, columns_range: List[str]) -> str:
        res: pd.Series = self.__data_frame.loc[self.__data_frame[column] == value][columns_range]
        norm_func = lambda data_array: [re.sub('[^A-Za-z0-9]+', '', i.replace('&', 'and').lower()) for i in data_array]
        first_value = norm_func(res.values[0])
        results: bool = all([norm_func(row) == first_value for row in res.values])
        if not results:
            return value
        else:
            return None
