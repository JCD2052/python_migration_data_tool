import os
import tkinter
import traceback
import re
from collections import defaultdict
from pathlib import Path
from threading import Thread
from tkinter import Tk, Button, Label, filedialog

import pandas as pd

from utils.label_logger import LabelLogger
from utils.excel_utils import *
from utils.string_utils import *
from utils.color_constants import *

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


sku_column_name = "MPSku"
lower_and_pattern = " and "


class IssueCategories:
    sku_duplicate = "SKU duplicate"
    lowercase_and = "Lowercase and"
    special_char = "Spectial char"
    non_breaking_space = "Non breaking space"
    trailing_space = "Trailing space"
    category_duplicate = "Category duplicate"
    similar_category = "Similar category"
    misspelled_word = "Misspelled word"


class CategoriesCorectnessApp:
    def __init__(self):
        self.__window = Tk()
        self.__select_data_file_label = self.__create_label_element('Select Excel file:')
        self.__select_data_file_button = Button(self.__window,
                                                   text=BUTTON_TEXT,
                                                   command=self.__select_data_file)
        
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
        keylist = [IssueCategories.sku_duplicate, IssueCategories.lowercase_and, IssueCategories.special_char,
                    IssueCategories.non_breaking_space, IssueCategories.trailing_space, IssueCategories.category_duplicate,
                    IssueCategories.similar_category, IssueCategories.misspelled_word]
        
        try:
            df_primary = pd.read_excel(self.__data_file_name, sheet_name=None)
            df = get_file_as_data_frame(self.__data_file_name)
            df = df.fillna('')

            to_color_dict = {key: [] for key in keylist}
            if(sku_column_name in df.columns):
                row_indexes = df[df[sku_column_name].duplicated() == True].index.values
                for row_index in row_indexes:
                    to_color_dict[IssueCategories.sku_duplicate].append((row_index, df.columns.get_loc(sku_column_name)))

            categories_primary_set = set()
            categories_updated_dict = defaultdict(set)
            for column_name in df.columns:
                if column_name == sku_column_name:
                    continue
                for index, category in df[column_name].items():
                    value = str(category)
                    value_updated = re.sub('&', 'And', value)
                    value_updated = re.sub('[ \,\-]', '', value_updated)
                    value_updated = value_updated.lower()
                    if value == '':
                        continue
                    if lower_and_pattern in value:
                        to_color_dict[IssueCategories.lowercase_and].append((index, df.columns.get_loc(column_name)))
                    elif not value_updated.isalnum():
                        to_color_dict[IssueCategories.special_char].append((index, df.columns.get_loc(column_name)))
                    elif "  " in value:
                        to_color_dict[IssueCategories.non_breaking_space].append((index, df.columns.get_loc(column_name)))
                    elif value.startswith(" ") or  value.endswith(" "):
                        to_color_dict[IssueCategories.trailing_space].append((index, df.columns.get_loc(column_name)))
                    
                    elif value not in categories_primary_set:
                        for set_of_categories in categories_updated_dict.values():
                            if(value_updated in set_of_categories and not ("  " in value or value.startswith(" ") or value.endswith(" "))):
                                to_color_dict[IssueCategories.similar_category].append((index, df.columns.get_loc(column_name)))

                    for key in categories_updated_dict.keys():
                        if(key == column_name):
                            continue
                        else:
                            if(value_updated in categories_updated_dict[key]):
                                to_color_dict[IssueCategories.category_duplicate].append((index, df.columns.get_loc(column_name)))
                    categories_updated_dict[column_name] |= {value_updated}
                    categories_primary_set.add(value)

            current_time = get_current_time_as_string()
            path = f"{self.__save_directory}/{current_time}"            
            
            with pd.ExcelWriter(f'{path}.xlsx') as writer:
                for key in df_primary:
                    df_primary[key].to_excel(writer, sheet_name=key, index=False)
                    df.style.apply(self.__style_specific_cell, dict=to_color_dict, axis=None).to_excel(writer, sheet_name="Marked", index=False)
            self.__status_label.info(f"Done. The file has been saved to {self.__save_directory}")
            self.__show_open_file_folder_button()
        
        except Exception:
            print(traceback.format_exc())
            self.__status_label.error(
                f"ERROR. SOMETHING WENT WRONG: {traceback.format_exc()}")

    def __style_specific_cell(self, x, dict):
                data_frame = pd.DataFrame('', index=x.index, columns=x.columns)
                for key in dict.keys():
                    match key:
                        case IssueCategories.sku_duplicate:
                            color = 'background-color: lightgreen'
                            for cell in dict[IssueCategories.sku_duplicate]:
                                data_frame.iloc[cell[0], cell[1]] = color
                        case IssueCategories.lowercase_and:
                            color = 'background-color: yellow'
                            for cell in dict[IssueCategories.lowercase_and]:
                                data_frame.iloc[cell[0], cell[1]] = color
                        case IssueCategories.special_char:
                            color = 'background-color: red'
                            for cell in dict[IssueCategories.special_char]:
                                data_frame.iloc[cell[0], cell[1]] = color
                        case IssueCategories.non_breaking_space:
                            color = 'background-color: blue'
                            for cell in dict[IssueCategories.non_breaking_space]:
                                data_frame.iloc[cell[0], cell[1]] = color
                        case IssueCategories.trailing_space:
                            color = 'background-color: lightblue'
                            for cell in dict[IssueCategories.trailing_space]:
                                data_frame.iloc[cell[0], cell[1]] = color
                        case IssueCategories.category_duplicate:
                            color = 'background-color: green'
                            for cell in dict[IssueCategories.category_duplicate]:
                                data_frame.iloc[cell[0], cell[1]] = color
                        case IssueCategories.similar_category:
                            color = 'background-color: orange'
                            for cell in dict[IssueCategories.similar_category]:
                                data_frame.iloc[cell[0], cell[1]] = color
                        case IssueCategories.misspelled_word:
                            color = 'background-color: lightred'
                            for cell in dict[IssueCategories.misspelled_word]:
                                data_frame.iloc[cell[0], cell[1]] = color
                return data_frame
    
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
            text=f"Selected P1 data file: {self.__get_file_name_from_path(self.__data_file_name)}")
            
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
                                          title="Select a File",
                                          filetypes=(("Excel files",
                                                      "*.xls*"),))

    # Get last used row
    def __get_rows_size(self) -> int:
        return self.__window.grid_size()[1]

    # Receive string value from entered path
    @staticmethod
    def __get_file_name_from_path(path: str) -> str:
        return Path(path).name
