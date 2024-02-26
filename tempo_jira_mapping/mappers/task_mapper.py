from collections import ChainMap
from typing import Dict
from tempo_jira_mapping.mappers.base_mapper import BaseMapper
from tempo_jira_mapping.columns.column_names import *


class TaskMapper(BaseMapper):
    _WORK_COLUMN = ISSUE_KEY_COLUMN_KEY
    _MAPPER_COLUMN = A1QA_ISSUE_COLUMN_KEY
    __DEFAULT_EPIC = 'Random epic'

    def _map_value(self, value: str) -> str:
        results = list(filter(lambda x: x[ISSUE_TEMPO_COLUMN_KEY] == value,
                              self._data_frame_to_list_of_dicts(self._mapping_data_frame)))
        row = results[0] if results else self._get_default_task()
        return row[self._MAPPER_COLUMN]

    def _get_default_task(self) -> Dict[str, str]:
        results = self._mapping_data_frame[
            self._mapping_data_frame[ISSUE_TEMPO_COLUMN_KEY] == self.__DEFAULT_EPIC]
        return dict(ChainMap(*self._data_frame_to_list_of_dicts(results)))
