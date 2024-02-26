import json
import pandas

from pandas import DataFrame

from tempo_jira_mapping.columns.column_names import *
from tempo_jira_mapping.mappers.base_mapper import BaseMapper
from utils.source_dir_reader import get_file_path_from_sources


class TempoToJira:
    __MAPPING_PATH = get_file_path_from_sources('column_mapping.json')
    __JIRA_TIME_FORMAT = '%m/%d/%Y'
    __WORK_COLUMNS = [ISSUE_KEY_COLUMN_KEY, ISSUE_SUMMARY_COLUMN_KEY, HOURS_COLUMN_KEY,
                      WORK_DATE_COLUMN_KEY,
                      FULL_NAME_COLUMN_KEY]

    def __init__(self, main_data_frame: DataFrame, *mappers: BaseMapper):
        self.__main_data_frame = main_data_frame[self.__WORK_COLUMNS]
        self.__mappers = mappers

    def process(self):
        self.__main_data_frame[CATEGORY_COLUMN_KEY] = self.__main_data_frame[
            ISSUE_KEY_COLUMN_KEY]
        for mapper in self.__mappers:
            mapper.apply_map_data_frame(self.__main_data_frame)
        else:
            self.__convert_time()
            self.__convert_date()
            return self.__main_data_frame.rename(columns=(self.__get_column_mapping()))

    def __convert_time(self):
        self.__main_data_frame[HOURS_COLUMN_KEY] = (self.__main_data_frame[HOURS_COLUMN_KEY]
                                                    .apply(lambda time: time * 60))

    def __convert_date(self):
        self.__main_data_frame[WORK_DATE_COLUMN_KEY] = pandas.to_datetime(
            self.__main_data_frame[WORK_DATE_COLUMN_KEY]).dt.strftime(self.__JIRA_TIME_FORMAT)

    def __get_column_mapping(self) -> dict:
        file = open(self.__MAPPING_PATH, 'r')
        return json.loads(file.read())
