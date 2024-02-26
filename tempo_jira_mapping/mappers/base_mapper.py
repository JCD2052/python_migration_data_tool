from abc import ABC, abstractmethod
from typing import List, Dict
from pandas import DataFrame
from utils.string_utils import EMPTY_STRING


class BaseMapper(ABC):
    _WORK_COLUMN = EMPTY_STRING
    _WORK_COLUMN: str

    def __init__(self, mapping_data_frame: DataFrame) -> None:
        self._mapping_data_frame = mapping_data_frame

    @abstractmethod
    def _map_value(self, value: str) -> str:
        pass

    def apply_map_data_frame(self, data_frame: DataFrame) -> None:
        for v in data_frame[self._WORK_COLUMN].unique():
            data_frame.loc[(data_frame[self._WORK_COLUMN] == v, self._WORK_COLUMN)] = self._map_value(v)

    @staticmethod
    def _data_frame_to_list_of_dicts(data_frame: DataFrame) -> List[Dict[(str, str)]]:
        return list(data_frame.to_dict('index').values())
