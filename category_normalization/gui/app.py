import os
import subprocess
import sys
import tkinter
import traceback
from pathlib import Path
from threading import Thread
from tkinter import Tk, Button, Label, filedialog

from category_normalization.data_manipulation.file_validation_strategy import BaseFileValidationStrategy
from category_normalization.data_manipulation.strategy_factory import StrategyFactory
from utils.color_constants import *
from utils.excel_utils import *
from utils.label_logger import LabelLogger
from utils.string_utils import EMPTY_STRING

APP_TITLE = 'Category Validation Tool'
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
FILE_PREFIX = "TestResults"


class CategoryNormalizationApp:
    def __init__(self):
        self.__window = Tk()
        self.__select_data_file_label = self.__create_label_element('Select Excel file:')
        self.__select_data_file_button = Button(self.__window,
                                                text=BUTTON_TEXT,
                                                command=self.__select_data_file)

        self.__submit_button = Button(self.__window,
                                      text="Submit",
                                      width=SUBMIT_WIDTH, height=SUBMIT_HEIGHT,
                                      command=self.__wrap_submit_command_into_thread)

        self.__open_file_folder_button = None
        self.__status_label = LabelLogger(self.__create_label_element(EMPTY_STRING))

        self.__data_file_name = EMPTY_STRING
        self.__last_position_in_grid = None

    def run(self):
        self.__configure_app()
        self.__configure_grid()
        self.__window.mainloop()

    # Configure app
    def __configure_app(self):
        self.__window.title(APP_TITLE)
        self.__window.geometry(WINDOW_GEOMETRY)
        self.__window.config(background=WHITE_COLOR)

    # Configure grid
    def __configure_grid(self):
        widgets = {k: v for k, v in self.__dict__.items() if issubclass(type(v), tkinter.Widget) and not None}.keys()
        for index, widget in enumerate(widgets):
            self.__getattribute__(widget).grid(column=DEFAULT_COLUMN, row=index)
            self.__window.rowconfigure(index, minsize=40)

        self.__status_label.element.grid(column=DEFAULT_COLUMN, row=self.__get_rows_size() + 1)
        self.__last_position_in_grid = self.__get_rows_size()

    # Wrap a submit logic into separated thread
    def __wrap_submit_command_into_thread(self) -> None:
        return Thread(target=self.__submit, daemon=True).start()

    # Main logic when user press submit
    def __submit(self) -> None:
        try:
            self.__status_label.info(f'Started validation of the table {Path(self.__data_file_name).name}...')
            data_frame = get_file_as_data_frame(self.__data_file_name)
            data_frame = data_frame.fillna('')
            self.__status_label.info('Read file...')
            validation_strategy: BaseFileValidationStrategy = StrategyFactory.get_strategy(data_frame,
                                                                                           self.__status_label)
            self.__status_label.info('Selected validation strategy...')
            validation_strategy.process()
            self.__status_label.info('Processed...')
            errors_data = validation_strategy.get_errors_frame()
            self.__status_label.info('Collected errors...')
            validated_data = validation_strategy.get_validated_frame()
            self.__status_label.info('Validated table...')
            legend_data = validation_strategy.get_legend_frame()
            self.__status_label.info('Created legend sheet...')
            new_file_path = self.__create_path_for_new_file()
            with pd.ExcelWriter(new_file_path, engine='openpyxl') as writer:
                self.__status_label.info(f'Saving tabs.....')
                validated_data.to_excel(writer,
                                        sheet_name="Validated", index=False, engine='openpyxl')
                errors_data.to_excel(writer,
                                     sheet_name="Errors", index=False, engine='openpyxl')
                legend_data.to_excel(writer,
                                     sheet_name="Criteria", index=False, engine='openpyxl')
            self.__status_label.info('Results have been saved.')
            self.__show_open_file_folder_button()
        except Exception:
            print(traceback.format_exc())
            self.__status_label.error(f"ERROR. SOMETHING WENT WRONG: {traceback.format_exc()}")

    # Logic when user presses select file
    def __select_data_file(self) -> None:
        self.__data_file_name = self.__open_excel_file_via_dialog()
        self.__select_data_file_label.configure(
            text=f"Selected data file: {Path(self.__data_file_name).name}")

    # Show open selected directory after main logic
    def __show_open_file_folder_button(self) -> None:
        self.__open_file_folder_button = Button(self.__window,
                                                text="Open file folder")
        self.__open_file_folder_button.grid(column=DEFAULT_COLUMN, row=self.__last_position_in_grid)
        self.__open_file_folder_button.configure(command=self.__open_file_folder)

    def __create_path_for_new_file(self):
        return Path(os.path.dirname(self.__data_file_name),
                    f"{FILE_PREFIX}_{Path(self.__data_file_name).name}")

    # Get save directory
    def __open_file_folder(self):
        file_folder = os.path.dirname(self.__data_file_name)
        if sys.platform == 'win32':
            return subprocess.check_call(['explorer', os.path.normpath(file_folder)])
        elif sys.platform == 'linux2':
            return subprocess.check_call(['xdg-open', '--', file_folder])
        elif sys.platform == 'darwin':
            return subprocess.check_call(['open', '--', file_folder])
        else:
            raise Exception("Unsupported platform")

    # Create label
    def __create_label_element(self, text) -> Label:
        return Label(self.__window,
                     text=text,
                     width=LABEL_WIDTH, height=LABEL_HEIGHT,
                     fg=BLUE_COLOR, background=WHITE_COLOR,
                     wraplength=WRAP_LENGTH)

    # Get last used row
    def __get_rows_size(self) -> int:
        return self.__window.grid_size()[1]

    # Open file with window dialog and save directory
    @staticmethod
    def __open_excel_file_via_dialog() -> str:
        return filedialog.askopenfilename(title="Select a file")
