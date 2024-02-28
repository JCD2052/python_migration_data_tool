import json
import os
import subprocess
import sys
import tkinter
import traceback
from pathlib import Path
from threading import Thread
from tkinter import Tk, Button, Label, filedialog
from typing import List

from tempo_jira_mapping.mappers.base_mapper import BaseMapper
from tempo_jira_mapping.mappers.category_mapper import CategoryMapper
from tempo_jira_mapping.mappers.task_mapper import TaskMapper
from tempo_jira_mapping.mappers.name_mapper import NameMapper
from tempo_jira_mapping.mappers.tempo_to_a1qa_mapper import TempoToJira
from utils.color_constants import *
from utils.excel_utils import *
from utils.label_logger import LabelLogger
from utils.source_dir_reader import get_file_path_from_sources
from utils.string_utils import EMPTY_STRING
from utils.string_utils import get_current_time_as_string

APP_TITLE = 'Tempo To Jira Mapper'
WINDOW_GEOMETRY = '600x300'
BUTTON_TEXT = 'Select File'
LABEL_HEIGHT = 4
LABEL_WIDTH = 80
SUBMIT_HEIGHT = 2
SUBMIT_WIDTH = 10
WRAP_LENGTH = 500
ROW_STEP = 3
DEFAULT_COLUMN = 1
EXCEL_FILE_EXTENSION = '.xlsx'
FILE_PREFIX = 'TestResults'


class TempoToJiraApp:

    def __init__(self):
        self.__window = Tk()
        self.__select_data_file_label = self.__create_label_element('Select Excel file:')
        self.__select_data_file_button = Button(self.__window, text=BUTTON_TEXT,
                                                command=self.__select_data_file)
        self.__submit_button = Button(self.__window, text='Submit',
                                      width=SUBMIT_WIDTH,
                                      height=SUBMIT_HEIGHT,
                                      command=self.__wrap_submit_command_into_thread)
        self.__open_file_folder_button = None
        self.__status_label = LabelLogger(self.__create_label_element(EMPTY_STRING))
        self.__data_file_name = EMPTY_STRING
        self.__last_position_in_grid = None

    def run(self):
        self.__configure_app()
        self.__configure_grid()
        self.__window.mainloop()

    def __configure_app(self):
        self.__window.title(APP_TITLE)
        self.__window.geometry(WINDOW_GEOMETRY)
        self.__window.config(background=WHITE_COLOR)

    def __configure_grid(self):
        widgets = {k: v for k, v in self.__dict__.items() if issubclass(type(v), tkinter.Widget) and not None}.keys()
        for index, widget in enumerate(widgets):
            self.__getattribute__(widget).grid(column=DEFAULT_COLUMN, row=index)
            self.__window.rowconfigure(index, minsize=40)

        self.__status_label.element.grid(column=DEFAULT_COLUMN, row=self.__get_rows_size() + 1)
        self.__last_position_in_grid = self.__get_rows_size()

    def __wrap_submit_command_into_thread(self) -> None:
        return Thread(target=self.__submit, daemon=True).start()

    def __submit(self) -> None:
        try:
            template_columns = get_file_as_data_frame(self.__get_template_file_path()).columns
            data_frame = get_file_as_data_frame(self.__data_file_name)
            self.__status_label.info('Read file...')
            data_frame = TempoToJira(data_frame, *self.__create_mappers()).process()
            for column in set(template_columns).difference(set(data_frame.columns)):
                data_frame[column] = {}
            data_frame = data_frame.fillna(EMPTY_STRING)
            data_frame = data_frame[template_columns]
            new_file_path = self.__create_path_for_new_file()
            with pd.ExcelWriter(new_file_path, engine='openpyxl') as writer:
                data_frame = data_frame.style.applymap(
                    lambda x: 'background-color : red' if 'Error' in str(x) else EMPTY_STRING)
                data_frame.to_excel(writer, sheet_name=self.__get_app_config()['work_logs_sheet_name'],
                                    index=False, engine='openpyxl')
            self.__status_label.info('Results have been saved.')
            self.__show_open_file_folder_button()

        except Exception as e:
            print(traceback.format_exc())
            self.__status_label.error(f"ERROR. SOMETHING WENT WRONG.\n\n{str(e)}")

    def __create_mappers(self) -> List[BaseMapper]:
        app_config = self.__get_app_config()
        template_file_path = self.__get_template_file_path()
        sheet_mapping = app_config['mapping_sheets']
        return [
            NameMapper(get_file_as_data_frame(template_file_path, sheet_mapping['name_mapping'])),
            TaskMapper(get_file_as_data_frame(template_file_path, sheet_mapping['tasks_mapping'])),
            CategoryMapper(get_file_as_data_frame(template_file_path, sheet_mapping['category_mapping']))]

    def __select_data_file(self) -> None:
        self.__data_file_name = self.__open_excel_file_via_dialog()
        self.__select_data_file_label.configure(text=f"Selected data file: {Path(self.__data_file_name).name}")

    def __show_open_file_folder_button(self) -> None:
        self.__open_file_folder_button = Button(self.__window, text='Open file folder')
        self.__open_file_folder_button.grid(column=DEFAULT_COLUMN, row=self.__last_position_in_grid)
        self.__open_file_folder_button.configure(command=self.__open_file_folder)

    def __create_path_for_new_file(self):
        return Path(os.path.dirname(self.__data_file_name),
                    f'Converted_logs_{get_current_time_as_string()}.{EXCEL_FILE_EXTENSION}')

    def __open_file_folder(self):
        file_folder = os.path.dirname(self.__data_file_name)
        if sys.platform == 'win32':
            return subprocess.check_call(['explorer', os.path.normpath(file_folder)])
        if sys.platform == 'linux2':
            return subprocess.check_call(['xdg-open', '--', file_folder])
        if sys.platform == 'darwin':
            return subprocess.check_call(['open', '--', file_folder])
        raise Exception('Unsupported platform')

    def __create_label_element(self, text) -> Label:
        return Label(self.__window, text=text,
                     width=LABEL_WIDTH,
                     height=LABEL_HEIGHT,
                     fg=BLUE_COLOR,
                     background=WHITE_COLOR,
                     wraplength=WRAP_LENGTH)

    def __get_rows_size(self) -> int:
        return self.__window.grid_size()[1]

    @staticmethod
    def __open_excel_file_via_dialog() -> str:
        return filedialog.askopenfilename(title='Select a file')

    @staticmethod
    def __get_template_file_path() -> str:
        return TempoToJiraApp.__get_app_config()['template_filepath']

    @staticmethod
    def __get_app_config() -> dict:
        file = open(get_file_path_from_sources('app_config.json'), 'r')
        return json.load(file)
