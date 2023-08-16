import os
import tkinter
from pathlib import Path
from threading import Thread
from tkinter import Tk, Button, Label, filedialog

import pandas as pd

from utils.label_logger import LabelLogger
from utils.excel_utils import save_data_data_frame_as_excel_file_to_path
from utils.string_utils import *
from utils.color_constants import *

APP_TITLE = 'Data Migration Tool'
WINDOW_GEOMETRY = '600x700'
BUTTON_TEXT = 'Select File'
LABEL_HEIGHT = 2
LABEL_WIDTH = 80
SUBMIT_HEIGHT = 2
SUBMIT_WIDTH = 10
WRAP_LENGTH = 600
ROW_STEP = 3
DEFAULT_COLUMN = 1

FIELDS_TO_SELECT_AFTER_MERGE = ['mirakl-product-sku-p1', 'mirakl-product-sku-p2', 'mirakl-product-id-p2']

MISMATCH_NO_AID_FILENAME = 'p1-p2-missmatch_noAID'
MISMATCH_AID_FILE_NAME = 'p1-p2-missmatch_AIDs'
MISSMATCH_FILE_NAME = "p1-p2-missmatch"
MAPPING_FILE_NAME = 'p1-p2-mapping'

NAN_VALUE = '----NO_AID---'
SEPARATOR = ';'

MIRAKL_SOURCES_TABLE_KEY = 'miraklsources'
MIRAKL_PRODUCT_SKU_TABLE_KEY = 'mirakl-product-sku'
MANUFACTURER_AID_TABLE_KEY = 'manufacturerAID'

SKU_SHOP_TABLE_KEYS = ['shop', 'sku']
FIELDS_TO_RENAME = {'mirakl-sources': MIRAKL_SOURCES_TABLE_KEY}
MIRAKL_MANDATORY_FIELDS = [MIRAKL_PRODUCT_SKU_TABLE_KEY, 'mirakl-product-id']
FIELDS_TO_MATCH_WITH = MIRAKL_MANDATORY_FIELDS + ['mirakl-sources', 'name [en]'] + [MANUFACTURER_AID_TABLE_KEY]
SHOP_DICT = {'2006': '2007',
             '2002': '2004',
             '2009': '2012',
             '2005': '2006',
             '2004': '2009',
             '2003': '2005',
             '2016': '2018',
             '2015': '2014',
             '2012': '2016',
             '2001': '2003',
             '2000': '2001',
             '2014': '2013'}


class SkuComparativeApp:
    def __init__(self):
        self.__window = Tk()
        self.__select_p1_data_file_label = self.__create_label_element('Select Excel file with P1 data:')
        self.__select_p1_data_file_button = Button(self.__window,
                                                   text=BUTTON_TEXT,
                                                   command=self.__select_p1_data_file)
        self.__select_p2_data_file_label = self.__create_label_element('Select Excel file with P2 data:')
        self.__select_p2_data_file_button = Button(self.__window,
                                                   text=BUTTON_TEXT,
                                                   command=self.__select_p2_data_file)
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

        self.__p1_data_file_name = EMPTY_STRING
        self.__p2_data_file_name = EMPTY_STRING
        self.__dev_data_file_name = EMPTY_STRING
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
            p1 = self.__read_csv_as_data_frame(self.__p1_data_file_name)
            p1 = self.__normalize_table(p1, 'p1')
            p1 = p1.replace({"shop": SHOP_DICT})
            p1 = p1.dropna(subset=["mirakl-product-sku-p1"]).drop_duplicates(
                subset=SKU_SHOP_TABLE_KEYS + [MANUFACTURER_AID_TABLE_KEY], keep=False)

            # p2
            p2 = self.__read_csv_as_data_frame(self.__p2_data_file_name)
            p2 = self.__normalize_table(p2, 'p2')
            p2 = p2.dropna(subset=["mirakl-product-sku-p2"]).drop_duplicates(
                subset=SKU_SHOP_TABLE_KEYS + [MANUFACTURER_AID_TABLE_KEY], keep=False)

            products_merged = p1.merge(p2, how='inner', on=SKU_SHOP_TABLE_KEYS + [MANUFACTURER_AID_TABLE_KEY])[
                FIELDS_TO_SELECT_AFTER_MERGE]
            products_merged_no_aid = p1.merge(p2, how='inner', on=SKU_SHOP_TABLE_KEYS)[FIELDS_TO_SELECT_AFTER_MERGE]

            self.__save_data_to_excel(products_merged, MAPPING_FILE_NAME)

            outer = p2[~p2['mirakl-product-sku-p2'].isin(products_merged['mirakl-product-sku-p2'])]
            outer = outer.merge(p1, how='inner', on=SKU_SHOP_TABLE_KEYS)
            self.__save_data_to_excel(outer, MISSMATCH_FILE_NAME)

            outer_aid_compare = outer['manufacturerAID_x'].compare(outer['manufacturerAID_y'])
            outer_aid_compare[MIRAKL_SOURCES_TABLE_KEY] = outer['miraklsources_x']
            self.__save_data_to_excel(outer_aid_compare, MISMATCH_AID_FILE_NAME)

            outer_no_aid = p2[~p2['mirakl-product-sku-p2'].isin(products_merged_no_aid['mirakl-product-sku-p2'])]
            self.__save_data_to_excel(outer_no_aid, MISMATCH_NO_AID_FILENAME)
            self.__status_label.info(f"Done. The file has been saved to {self.__save_directory}")
            self.__show_open_file_folder_button()
        except Exception as e:
            self.__status_label.error(
                f"ERROR. SOMETHING WENT WRONG: {type(e)} - {str(e.with_traceback(e.__traceback__))}")

    # Save final result data to excel
    def __save_data_to_excel(self, data: pd.DataFrame, prefix: str = None) -> None:
        if prefix is None:
            prefix = ''
        current_time = get_current_time_as_string()
        path = f"{self.__save_directory}/{prefix}_{current_time}"
        self.__status_label.info(f'Saving file to {path}...')
        save_data_data_frame_as_excel_file_to_path(data, path)
        self.__status_label.info(f"Done. The file has been saved to {path}")

    # Logic when user presses select 1 file
    def __select_p1_data_file(self) -> None:
        self.__p1_data_file_name = self.__open_excel_file_via_dialog()
        self.__last_opened_directory = self.__p1_data_file_name
        self.__select_p1_data_file_label.configure(
            text=f"Selected P1 data file: {self.__get_file_name_from_path(self.__p1_data_file_name)}")

    # Logic when user presses select p2 file
    def __select_p2_data_file(self) -> None:
        self.__p2_data_file_name = self.__open_excel_file_via_dialog()
        self.__last_opened_directory = self.__p2_data_file_name
        self.__select_p2_data_file_label.configure(
            text=f"Selected P2 data file: {self.__get_file_name_from_path(self.__p2_data_file_name)}")

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
                                                      "*.csv*"),))

    # Get last used row
    def __get_rows_size(self) -> int:
        return self.__window.grid_size()[1]

    # Read .csv file as dataFr
    @staticmethod
    def __read_csv_as_data_frame(path: str) -> pd.DataFrame:
        return pd.read_csv(path, on_bad_lines='skip', sep=SEPARATOR, usecols=FIELDS_TO_MATCH_WITH).rename(
            columns=FIELDS_TO_RENAME)

    # Normalize input data_frame: remaining column names according to table_name, split values,
    # replace empty cells with the new value
    @staticmethod
    def __normalize_table(data_frame: pd.DataFrame, table_name: str) -> pd.DataFrame:
        data_frame = data_frame.rename(columns={field: f'{field}-{table_name}' for field in MIRAKL_MANDATORY_FIELDS})
        data_frame[MIRAKL_SOURCES_TABLE_KEY] = data_frame[MIRAKL_SOURCES_TABLE_KEY].str.split(',')
        data_frame = data_frame.explode(MIRAKL_SOURCES_TABLE_KEY)
        data_frame[SKU_SHOP_TABLE_KEYS] = data_frame[MIRAKL_SOURCES_TABLE_KEY].str.split("|", n=1, expand=True)
        data_frame[MANUFACTURER_AID_TABLE_KEY].fillna(NAN_VALUE, inplace=True)

        return data_frame

    # Receive string value from entered path
    @staticmethod
    def __get_file_name_from_path(path: str) -> str:
        return Path(path).name
