from tempo_jira_mapping.columns.column_names import *
from tempo_jira_mapping.mappers.base_mapper import BaseMapper


class NameMapper(BaseMapper):
    _NameMapper__MESSAGE_TEMPLATE = "Error. Couldn't find a mapping for a user:"
    _MAP_NAME = A1QA_USERNAME_COLUMN_KEY
    _WORK_COLUMN = FULL_NAME_COLUMN_KEY

    def _map_value(self, value: str) -> str:
        results = list(filter(lambda x: x[TEMPO_USERNAME_COLUMN_KEY] == value,
                              self._data_frame_to_list_of_dicts(self._mapping_data_frame)))
        if results:
            return results[0][self._MAP_NAME]
        return f"{self._NameMapper__MESSAGE_TEMPLATE} {value}"
