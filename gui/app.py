import tkinter
from threading import Thread
from tkinter import filedialog, Tk, Button, Label, StringVar, OptionMenu
from pathlib import Path
import os

import numpy

from gui.label_logger import LabelLogger
from utils.excel_utils import *
from utils.string_utils import *
from utils.color_constants import *

APP_TITLE = 'Data Migration Tool'
WINDOW_GEOMETRY = '600x600'
BUTTON_TEXT = 'Select File'
LABEL_HEIGHT = 2
LABEL_WIDTH = 80
SUBMIT_HEIGHT = 2
SUBMIT_WIDTH = 10
WRAP_LENGTH = 600
ROW_STEP = 3
DEFAULT_COLUMN = 1

DISABLED_STATE = 'disabled'
START_MESSAGE_FOR_DROPDOWN_LABEL = 'Please, load the file with blank template'

BRAND_COLUMN_KEY = 'brand'
SKU_COLUMN_KEY = 'sku'

MIRAKL_PRODUCT_POSTFIX = '_0001'
LEFT_SUFFIX = 'merge_left_suffix'
RIGHT_SUFFIX = 'merge_right_suffix'
SKU_POSTFIX = '_01'
QUANTITY = '50000'


class DataMigrationApp:
    def __init__(self):
        self.__window = Tk()
        self.__select_template_file_label = self.__create_label_element('Select Excel file with blank template:')
        self.__select_template_file_button = Button(self.__window,
                                                    text=BUTTON_TEXT,
                                                    command=self.__select_template_file)
        self.__select_product_data_file_label = self.__create_label_element('Select Excel file with product data:')
        self.__select_product_data_file_button = Button(self.__window,
                                                        text=BUTTON_TEXT,
                                                        command=self.__select_product_data_file)
        self.__select_mirakl_product_data_file_label = self.__create_label_element(
            'Select Excel file with Mirakl data:')
        self.__select_mirakl_product_data_file_button = Button(self.__window,
                                                               text=BUTTON_TEXT,
                                                               command=self.__select_mirakl_data_file)
        self.__browse_save_directory_label = self.__create_label_element('Select a folder to save the file:')
        self.__browse_save_directory_button = Button(self.__window,
                                                     text="Select Directory",
                                                     command=self.__select_save_directory)

        self.__product_id_dropdown_var = StringVar()
        self.__select_product_id_type_label = self.__create_label_element(START_MESSAGE_FOR_DROPDOWN_LABEL)
        self.__product_id_type_dropdown = OptionMenu(self.__window, self.__product_id_dropdown_var, EMPTY_STRING)
        self.__state_dropdown_var = StringVar()
        self.__select_state_label = self.__create_label_element(START_MESSAGE_FOR_DROPDOWN_LABEL)
        self.__state_dropdown = OptionMenu(self.__window, self.__state_dropdown_var, EMPTY_STRING)
        self.__category_dropdown_var = StringVar()
        self.__select_category_label = self.__create_label_element(START_MESSAGE_FOR_DROPDOWN_LABEL)
        self.__category_dropdown = OptionMenu(self.__window, self.__category_dropdown_var, EMPTY_STRING)
        self.__status_label = LabelLogger(self.__create_label_element(EMPTY_STRING))

        self.__submit_button = Button(self.__window,
                                      text="Submit",
                                      width=SUBMIT_WIDTH, height=SUBMIT_HEIGHT,
                                      command=self.__wrap_submit_command_into_thread)

        self.__open_file_folder_button = None

        self.__template_file_name = EMPTY_STRING
        self.__product_data_file_name = EMPTY_STRING
        self.__mirakl_data_file_name = EMPTY_STRING
        self.__save_directory = EMPTY_STRING

        self.__reference_data_data_frame = None
        self.__last_opened_directory = "/"
        self.__last_position_in_grid = None

    def run(self):
        self.__configure_app()
        self.__configure_grid()
        self.__window.mainloop()

    def __configure_grid(self):
        widgets = {k: v for k, v in self.__dict__.items() if issubclass(type(v), tkinter.Widget) and not None}.keys()
        for index, widget in enumerate(widgets):
            self.__getattribute__(widget).grid(column=DEFAULT_COLUMN, row=index)
            self.__window.rowconfigure(index, minsize=40)
        self.__last_position_in_grid = len(widgets)

        dropdowns = {k: v for k, v in self.__dict__.items() if isinstance(type(v), tkinter.Menubutton)}.keys()
        for dropdown in dropdowns:
            self.__getattribute__(dropdown).configure(state=DISABLED_STATE)

    def __configure_app(self):
        self.__window.title(APP_TITLE)
        self.__window.geometry(WINDOW_GEOMETRY)
        self.__window.config(background=WHITE_COLOR)

    def __wrap_submit_command_into_thread(self):
        return Thread(target=self.__submit, daemon=True).start()

    def __submit(self):
        try:
            template_df = get_file_as_data_frame(self.__template_file_name)
            product_df = get_file_as_data_frame(self.__product_data_file_name)
            if list(product_df.columns) in list(template_df.columns):
                product_df = self.__drop_headers_from_data_frame(product_df)
            offer_df = self.__get__normalized_offer_data()
            data = pd.merge(template_df, product_df, how='right', on=list(product_df.columns))
            original_headers = data.columns
            data = self.__drop_headers_from_data_frame(data)
            data = self.merge_with_offer_data_and_normalize(data, offer_df)
            if not self.__product_id_dropdown_var.get():
                raise Exception("Product id hasn't been specified")
            elif not self.__category_dropdown_var.get():
                raise Exception("Category hasn't been specified")
            elif not self.__state_dropdown_var.get():
                raise Exception("State hasn't been specified")
            data = self.set_dropdown_values(data)
            data = self.insert_secondary_headers_as_row(data)
            data.columns = original_headers
            self.__save_data_to_excel(data)
            self.__show_open_file_folder_button()
        except Exception as e:
            self.__status_label.error(
                f"ERROR. SOMETHING WENT WRONG: {type(e)} - {str(e.with_traceback(e.__traceback__))}")

    def set_dropdown_values(self, data):
        data = data.assign(**{'category': self.__category_dropdown_var.get()})
        data['product-id-type'] = numpy.where(data[SKU_COLUMN_KEY] == EMPTY_STRING, EMPTY_STRING,
                                              self.__product_id_dropdown_var.get())
        data['state'] = numpy.where(data[SKU_COLUMN_KEY] == EMPTY_STRING, EMPTY_STRING,
                                    self.__state_dropdown_var.get())
        data['quantity'] = numpy.where(data[SKU_COLUMN_KEY] == EMPTY_STRING, EMPTY_STRING, QUANTITY)
        return data

    def __save_data_to_excel(self, data):
        current_time = get_current_time_as_string()
        path = f"{self.__save_directory}/{current_time}"
        save_data_data_frame_as_excel_file_to_path(data, path)
        self.__status_label.info(f"Done. The file has been saved to {path}")

    def __get__normalized_offer_data(self):
        offer_df = get_file_as_data_frame(self.__mirakl_data_file_name)
        # remove mirakl postfix from sku column values
        duplicates = offer_df[offer_df[SKU_COLUMN_KEY].str.contains(SKU_POSTFIX) == False].reset_index(drop=True)
        offer_df = offer_df[offer_df[SKU_COLUMN_KEY].str.contains(SKU_POSTFIX) == True].reset_index(drop=True)
        offer_df[SKU_COLUMN_KEY] = pd.Series(
            map(lambda sku: str(sku).replace(MIRAKL_PRODUCT_POSTFIX, EMPTY_STRING).replace(SKU_POSTFIX, EMPTY_STRING),
                offer_df[SKU_COLUMN_KEY].to_numpy()))
        offer_df = pd.merge(offer_df, duplicates, how='outer', on=list(offer_df.columns))
        return offer_df

    def __select_template_file(self):
        self.__template_file_name = self.__open_excel_file_via_dialog()
        self.__last_opened_directory = self.__template_file_name
        self.__select_template_file_label.configure(
            text=f"Selected File blank template: {self.__get_file_name_from_path(self.__template_file_name)}")

        self.__set_dropdown_with_values_from_reference_data()

    def __select_product_data_file(self):
        self.__product_data_file_name = self.__open_excel_file_via_dialog()
        self.__last_opened_directory = self.__product_data_file_name
        self.__select_product_data_file_label.configure(
            text=f"Selected Product Data File: {self.__get_file_name_from_path(self.__product_data_file_name)}")

    def __select_mirakl_data_file(self):
        self.__mirakl_data_file_name = self.__open_excel_file_via_dialog()
        self.__last_opened_directory = self.__mirakl_data_file_name
        self.__select_mirakl_product_data_file_label.configure(
            text=f"Selected Mirakl Data File: {self.__get_file_name_from_path(self.__mirakl_data_file_name)}")

    def __select_save_directory(self):
        self.__save_directory = filedialog.askdirectory()
        self.__last_opened_directory = self.__save_directory
        self.__browse_save_directory_label.configure(
            text="Selected Directory to save an output file: " + self.__save_directory)

    def __set_reference_data_data_frame(self):
        self.__reference_data_data_frame = get_file_as_data_frame(self.__template_file_name, 'ReferenceData')
        self.__reference_data_data_frame = self.__reference_data_data_frame.fillna(EMPTY_STRING)

    def __show_open_file_folder_button(self):
        self.__open_file_folder_button = Button(self.__window,
                                                text="Open file folder")
        self.__open_file_folder_button.grid(column=1, row=19)
        self.__open_file_folder_button.configure(command=self.__open_file_folder)

    def __open_file_folder(self):
        return os.startfile(self.__save_directory)

    def __set_dropdown_with_values_from_reference_data(self):
        self.__set_reference_data_data_frame()

        categories = self.__reference_data_data_frame['category']
        self.__set_dropdown_with_options(self.__category_dropdown, self.__category_dropdown_var, categories)
        self.__select_category_label.configure(text='Select category:')

        states = self.__reference_data_data_frame['state']
        self.__set_dropdown_with_options(self.__state_dropdown, self.__state_dropdown_var, states)
        self.__select_state_label.configure(text='Select state:')

        product_id_types = self.__reference_data_data_frame['product-id-type']
        self.__set_dropdown_with_options(self.__product_id_type_dropdown, self.__product_id_dropdown_var,
                                         product_id_types)
        self.__select_product_id_type_label.configure(text='Select product id type:')

    def __create_label_element(self, text):
        return Label(self.__window,
                     text=text,
                     width=LABEL_WIDTH, height=LABEL_HEIGHT,
                     fg=BLUE_COLOR, background=WHITE_COLOR,
                     wraplength=WRAP_LENGTH)

    def __open_excel_file_via_dialog(self):
        return filedialog.askopenfilename(initialdir=self.__last_opened_directory,
                                          title="Select a File",
                                          filetypes=(("Excel files",
                                                      "*.xls*"),))

    @staticmethod
    def merge_with_offer_data_and_normalize(data, offer_data):
        columns_with_valid_order = data.columns.to_numpy()
        data = pd.merge(data, offer_data, how='left', left_on='shop_sku', right_on=SKU_COLUMN_KEY,
                        suffixes=(LEFT_SUFFIX, RIGHT_SUFFIX))
        data = data.fillna(EMPTY_STRING)
        # remove created columns after merge
        cols = list(filter(lambda column: LEFT_SUFFIX not in str(column), data.columns))
        data = data[cols]
        data.columns = data.columns.str.replace(RIGHT_SUFFIX, EMPTY_STRING)
        data = data[columns_with_valid_order]
        # set entire 'product-id' column with values from 'sku' column
        data['product-id'] = data[SKU_COLUMN_KEY]
        # add sku postfix to 'sku' column values
        data[SKU_COLUMN_KEY] = pd.Series(
            map(lambda sku: EMPTY_STRING if not str(sku) else f'{str(sku)}{SKU_POSTFIX}',
                data[SKU_COLUMN_KEY].to_numpy()))
        return data

    @staticmethod
    def insert_secondary_headers_as_row(data):
        data.loc[-1] = data.columns  # adding a row
        data.index = data.index + 1  # shifting index
        return data.sort_index()

    @staticmethod
    def __drop_headers_from_data_frame(data_frame):
        data_frame.columns = data_frame.iloc[0]
        return data_frame.drop(data_frame.index[0])

    @staticmethod
    def __set_dropdown_with_options(dropdown_element, dropdown_var, options):
        options = filter(lambda cell: cell != EMPTY_STRING, options)
        dropdown_element.configure(state='normal')
        menu = dropdown_element['menu']
        menu.delete(0, 'end')
        for option in options:
            menu.add_command(label=option, command=lambda o=option: dropdown_var.set(o))

    @staticmethod
    def __get_file_name_from_path(path):
        return Path(path).name
