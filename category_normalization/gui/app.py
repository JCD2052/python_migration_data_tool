import os
import tkinter
import traceback
from pathlib import Path
from threading import Thread
from tkinter import Tk, Button, Label, filedialog
from shutil import copy

import pandas as pd

from utils.label_logger import LabelLogger
from utils.excel_utils import *
from utils.string_utils import *
from utils.color_constants import *
from category_normalization.validators.validators import *
SPACE_STRING = ' '
sku_column_name = "MPSku"

APP_TITLE = 'Data Migration Tool'
WINDOW_GEOMETRY = '600x500'
BUTTON_TEXT = 'Select File'
LABEL_HEIGHT = 2
LABEL_WIDTH = 80
SUBMIT_HEIGHT = 2
SUBMIT_WIDTH = 10
WRAP_LENGTH = 600
ROW_STEP = 3
DEFAULT_COLUMN = 1
EXCEL_FILE_EXTENSION = '.xlsx'


class CategoryNormalizationApp:
    def __init__(self):
        self.__window = Tk()
        self.__select_data_file_label = self.__create_label_element('Select Excel file:')
        self.__select_data_file_button = Button(self.__window,
                                                   text=BUTTON_TEXT,
                                                   command=self.__select_data_file)
        
        self.__select_words_file_label = self.__create_label_element('Select words file:')
        self.__select_words_file_button = Button(self.__window,
                                                   text=BUTTON_TEXT,
                                                   command=self.__select_words_file)
        
        self.__browse_save_directory_label = self.__create_label_element('Select a folder to save the file:')
        self.__browse_save_directory_button = Button(self.__window,
                                                     text="Select Directory",
                                                     command=self.__select_save_directory)

        self.__submit_button = Button(self.__window,
                                      text="Submit",
                                      width=SUBMIT_WIDTH, height=SUBMIT_HEIGHT,
                                      command=self.__wrap_submit_command_into_thread)

        self.__open_file_folder_button = None
        self.__status_label = LabelLogger(self.__create_label_element(EMPTY_STRING))

        self.__data_file_name = EMPTY_STRING
        self.__words_file_name = EMPTY_STRING
        self.__save_directory = EMPTY_STRING

        self.__last_opened_directory = "/"
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
            self.__status_label.info(f'Normalization of table {self.__get_file_name_from_path(self.__data_file_name)}...')
            current_time = get_current_time_as_string()
            path = f"{self.__save_directory}/{current_time}{EXCEL_FILE_EXTENSION}" 
            copy(self.__data_file_name, path)
            df = get_file_as_data_frame(path)
            df = df.fillna('')
            level_categories_columns = list(filter(lambda x: str(x).lower().startswith('l'), df.columns))
            unique_table_values = list(
                itertools.chain(*[list(filter(lambda x: bool(x), df[c].unique())) for c in level_categories_columns]))

            errors = dict()
            validators = [LowerAndValidator(),
                        SpecialCharactersValidator(),
                        ExtraSpacesValidator(),
                        NonBreakingSpaceValidator(),
                        SpellCheckValidator(),
                        AlmostSameWordValidator(unique_table_values),
                        DuplicatesInColumnValidator({col: v for col in level_categories_columns for v in df[col].unique()})]

            for column in level_categories_columns:
                for value in filter(lambda x: str(x), df[column].unique()):
                    res = [validator for validator in validators if validator.validate(value)]
                    res.sort(key=lambda x: x.get_priority())
                    if res:
                        errors.update({value: res[0].get_background_color()})

            for value in df[df[sku_column_name].duplicated() == True][sku_column_name].unique():
                if SkuDuplicateValidator().validate(value):
                    errors.update({value: SkuDuplicateValidator.get_background_color()})

            styled = df.style.applymap(lambda x: errors.get(x, None))

            with pd.ExcelWriter(path, mode="a") as writer:
                self.__status_label.info(f'Saving file to {path}...')
                styled.to_excel(writer, sheet_name="Normalized", index=False)
            self.__status_label.info(f"Done. The file has been saved to {self.__save_directory}")
            self.__show_open_file_folder_button()
        
        except Exception:
            self.__status_label.error(
                f"ERROR. SOMETHING WENT WRONG: {traceback.format_exc()}")
    
    # Save final result data to excel
    def __save_data_to_excel(self, data: pd.DataFrame, prefix: str = None) -> None:
        if prefix is None:
            prefix = ''
        current_time = get_current_time_as_string()
        path = f"{self.__save_directory}/{prefix}_{current_time}"
        self.__status_label.info(f'Saving file to {path}...')
        save_data_data_frame_as_excel_file_to_path(data, path)
        self.__status_label.info(f"Done. The file has been saved to {path}")

    # Logic when user presses select file
    def __select_data_file(self) -> None:
        self.__data_file_name = self.__open_excel_file_via_dialog()
        self.__last_opened_directory = self.__data_file_name
        self.__select_data_file_label.configure(
            text=f"Selected data file: {self.__get_file_name_from_path(self.__data_file_name)}")
        
    # Logic when user presses select file
    def __select_words_file(self) -> None:
        self.__words_file_name = self.__open_txt_file_via_dialog()
        SpellCheckValidator()._path_to_words_file = self.__words_file_name
        self.__last_opened_directory = self.__data_file_name
        self.__select_words_file_label.configure(
            text=f"Selected words file: {self.__get_file_name_from_path(self.__words_file_name)}")
            
    # Logic when user presses select save directory
    def __select_save_directory(self) -> None:
        self.__save_directory = filedialog.askdirectory()
        self.__last_opened_directory = self.__save_directory
        self.__browse_save_directory_label.configure(
            text="Selected Directory to save an output file: " + self.__save_directory)

    # Show open selected directory after main logic
    def __show_open_file_folder_button(self) -> None:
        self.__open_file_folder_button = Button(self.__window,
                                                text="Open file folder")
        self.__open_file_folder_button.grid(column=DEFAULT_COLUMN, row=self.__last_position_in_grid)
        self.__open_file_folder_button.configure(command=self.__open_file_folder)

    # Get save directory
    def __open_file_folder(self):
        return os.startfile(self.__save_directory)

    # Create label
    def __create_label_element(self, text) -> Label:
        return Label(self.__window,
                     text=text,
                     width=LABEL_WIDTH, height=LABEL_HEIGHT,
                     fg=BLUE_COLOR, background=WHITE_COLOR,
                     wraplength=WRAP_LENGTH)

    # Open file with window dialog and save directory
    def __open_excel_file_via_dialog(self) -> str:
        return filedialog.askopenfilename(initialdir=self.__last_opened_directory,
                                          title="Select a file",
                                          filetypes=(("Excel files",
                                                      "*.xls*"),))
    
    def __open_txt_file_via_dialog(self) -> str:
        return filedialog.askopenfilename(initialdir=self.__last_opened_directory,
                                          title="Select a file",
                                          filetypes=((f"Txt files",
                                                      f"*.txt*"),))

    # Get last used row
    def __get_rows_size(self) -> int:
        return self.__window.grid_size()[1]

    # Receive string value from entered path
    @staticmethod
    def __get_file_name_from_path(path: str) -> str:
        return Path(path).name
