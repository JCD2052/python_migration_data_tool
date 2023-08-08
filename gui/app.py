from threading import Thread
from tkinter import filedialog, Tk, Button, Label, StringVar, OptionMenu
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
WRAPLENGHT = 600

DISABLED_STATE = 'disabled'
START_MESSAGE_FOR_DROPDOWN_LABEL = 'Please, load the file with blank template'

BRAND_COLUMN_KEY = 'brand'
SKU_COLUMN_KEY = 'sku'

MIRAKL_PRODUCT_POST_FIX = '_0001'
LEFT_SUFFIX = 'merge_left_suffix'
RIGHT_SUFFIX = 'merge_right_suffix'
SKU_POSTFIX = '_01'
QUANTITY = '50000'


class DataMigrationApp:
    def __init__(self):
        self.__window = Tk()
        self.__select_template_file_label = self.__create_label_element('Select Excel file with blank template:')
        self.__select_product_data_file_label = self.__create_label_element('Select Excel file with product data:')
        self.__select_mirakl_product_data_file_label = self.__create_label_element('Select Excel file with Mirakl data:')
        self.__browse_save_directory_label = self.__create_label_element('Select a folder to save the file:')
        self.__select_category_label = self.__create_label_element(START_MESSAGE_FOR_DROPDOWN_LABEL)
        self.__select_state_label = self.__create_label_element(START_MESSAGE_FOR_DROPDOWN_LABEL)
        self.__select_product_id_type_label = self.__create_label_element(START_MESSAGE_FOR_DROPDOWN_LABEL)
        self.__blank_line_label = self.__create_label_element(EMPTY_STRING)
        self.__status_label = LabelLogger(self.__create_label_element(EMPTY_STRING))

        self.__select_product_data_file_button = Button(self.__window,
                                                        text=BUTTON_TEXT,
                                                        command=self.__select_product_data_file)
        
        self.__select_template_file_button = Button(self.__window,
                                                    text=BUTTON_TEXT,
                                                    command=self.__select_template_file)

        self.__select_mirakl_product_data_file_button = Button(self.__window,
                                                               text=BUTTON_TEXT,
                                                               command=self.__select_mirakl_data_file)
        
        self.__browse_save_directory_button = Button(self.__window,
                                                     text="Select Directory",
                                                     command=self.__select_save_directory)
        
        self.__submit_button = Button(self.__window,
                                      text="Submit",
                                      width=SUBMIT_WIDTH, height=SUBMIT_HEIGHT,
                                      command=self.__wrap_submit_command_into_thread)
        
        self.__open_file_folder_button = Button(self.__window,
                                      text="Open file folder")

        self.__product_id_dropdown_var = StringVar()
        self.__product_id_type_dropdown = OptionMenu(self.__window, self.__product_id_dropdown_var, EMPTY_STRING)
        self.__category_dropdown_var = StringVar()
        self.__category_dropdown = OptionMenu(self.__window, self.__category_dropdown_var, EMPTY_STRING)
        self.__state_dropdown_var = StringVar()
        self.__state_dropdown = OptionMenu(self.__window, self.__state_dropdown_var, EMPTY_STRING)

        self.__template_file_name = EMPTY_STRING
        self.__product_data_file_name = EMPTY_STRING
        self.__mirakl_data_file_name = EMPTY_STRING
        self.__save_directory = EMPTY_STRING

        self.__reference_data_data_frame = None

    def run(self):
        self.__configure_app()
        self.__configure_grid()
        self.__window.mainloop()

    def __configure_grid(self):
        self.__select_template_file_label.grid(column=1, row=1)
        self.__select_template_file_button.grid(column=1, row=2)
        self.__select_product_data_file_label.grid(column=1, row=3)
        self.__select_product_data_file_button.grid(column=1, row=4)
        self.__select_mirakl_product_data_file_label.grid(column=1, row=5)
        self.__select_mirakl_product_data_file_button.grid(column=1, row=6)
        self.__browse_save_directory_label.grid(column=1, row=7)
        self.__browse_save_directory_button.grid(column=1, row=8)
        self.__select_product_id_type_label.grid(column=1, row=9)
        self.__product_id_type_dropdown.grid(column=1, row=10)
        self.__product_id_type_dropdown.configure(state=DISABLED_STATE)
        self.__select_category_label.grid(column=1, row=11)
        self.__category_dropdown.grid(column=1, row=12)
        self.__category_dropdown.configure(state=DISABLED_STATE)
        self.__select_state_label.grid(column=1, row=13)
        self.__state_dropdown.grid(column=1, row=14)
        self.__state_dropdown.configure(state=DISABLED_STATE)
        self.__blank_line_label.grid(column=1, row=15)
        self.__submit_button.grid(column=1, row=17)
        self.__status_label.element.grid(column=1, row=18)

    def __configure_app(self):
        self.__window.title(APP_TITLE)
        self.__window.geometry(WINDOW_GEOMETRY)
        self.__window.config(background=WHITE_COLOR)

    def __wrap_submit_command_into_thread(self):
        return Thread(target=self.__submit, daemon=True).start()

    def __submit(self):
        try:
            # read Excel file with products
            product_df = get_file_as_data_frame(self.__product_data_file_name)
            # read Excel file with mirakl data
            offer_df = get_file_as_data_frame(self.__mirakl_data_file_name)
            # remove mirakl postfix from sku column values
            offer_df[SKU_COLUMN_KEY] = pd.Series(
                map(lambda sku: str(sku).replace(MIRAKL_PRODUCT_POST_FIX, EMPTY_STRING),
                    offer_df[SKU_COLUMN_KEY].to_numpy()))
            # read Excel file with template
            template_df = get_file_as_data_frame(self.__template_file_name)
            valid_brands = self.__reference_data_data_frame[BRAND_COLUMN_KEY]
            # merge product data table to with template
            data = pd.merge(template_df, product_df, how='right', on=list(product_df.columns))
            # save original headers
            original_headers = data.columns
            data.columns = data.iloc[0]
            data = data.drop(data.index[0])
            # save secondary headers in right orders
            columns_with_valid_order = data.columns.to_numpy()
            # merge result table from previous merge with mirakl data table
            data = pd.merge(data, offer_df, how='left', left_on='shop_sku', right_on=SKU_COLUMN_KEY,
                            suffixes=(LEFT_SUFFIX, RIGHT_SUFFIX))
            # replace NAN values in result table to empty string
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
                map(lambda sku: f'{str(sku)}{SKU_POSTFIX}' if str(sku) is not EMPTY_STRING else EMPTY_STRING,
                    data[SKU_COLUMN_KEY].to_numpy()))
            # set entire column with certain value
            if(self.__product_id_dropdown_var.get() == EMPTY_STRING):
                raise Exception("Product id hasn't been specified")
            elif(self.__category_dropdown_var.get() == EMPTY_STRING):
                raise Exception("Category hasn't been specified")
            elif(self.__state_dropdown_var.get() == EMPTY_STRING):
                raise Exception("State hasn't been specified")
            data = data.assign(**{'category': self.__category_dropdown_var.get()})            
            data['product-id-type'] = numpy.where(data[SKU_COLUMN_KEY] == EMPTY_STRING, EMPTY_STRING,
                                                  self.__product_id_dropdown_var.get())
            data['state'] = numpy.where(data[SKU_COLUMN_KEY] == EMPTY_STRING, EMPTY_STRING,
                                        self.__state_dropdown_var.get())
            data['quantity'] = numpy.where(data[SKU_COLUMN_KEY] == EMPTY_STRING, EMPTY_STRING, QUANTITY)
            # set valid brand values
            results_brand = []
            for index, brand in enumerate(data[BRAND_COLUMN_KEY].to_numpy()):
                brand_string = str(brand)
                res = find_string_in_lower_case_or_without_special_characters(brand_string, valid_brands)
                self.__status_label.info(f'{res} has been found for {brand_string} at index {index}')
                results_brand.append(res)
            data[BRAND_COLUMN_KEY] = pd.Series(results_brand)
            # add back original header row
            data.loc[-1] = data.columns  # adding a row
            data.index = data.index + 1  # shifting index
            data = data.sort_index()
            data.columns = original_headers
            # save result table to Excel file
            current_time = get_current_time_as_string()
            path = f"{self.__save_directory}/{current_time}"
            save_data_data_frame_as_excel_file_to_path(data, path)
            self.__status_label.info(f"Done. The file has been saved to {path}")

            # add open file folder button
            self.__open_file_folder_button.grid(column=1, row=19)
            self.__open_file_folder_button.configure(command=self.__open_file_folder)
            
        except Exception as e:
            self.__status_label.error(f"ERROR. SOMETHING WENT WRONG {str(e)}")

    def __select_template_file(self):
        self.__template_file_name = self.__open_excel_file_via_dialog()
        self.__select_template_file_label.configure(
            text="Selected File blank template: " + f"\"{self.__template_file_name.split('/')[-1]}\"")

        self.__set_dropdown_with_values_from_reference_data()

    def __select_product_data_file(self):
        self.__product_data_file_name = self.__open_excel_file_via_dialog()
        self.__select_product_data_file_label.configure(
            text="Selected Product Data File: " + f"\"{self.__product_data_file_name.split('/')[-1]}\"")

    def __select_mirakl_data_file(self):
        self.__mirakl_data_file_name = self.__open_excel_file_via_dialog()
        self.__select_mirakl_product_data_file_label.configure(
            text="Selected Mirakl Data File: " + f"\"{self.__mirakl_data_file_name.split('/')[-1]}\"")

    def __select_save_directory(self):
        self.__save_directory = filedialog.askdirectory()
        self.__browse_save_directory_label.configure(
            text="Selected Directory to save an output file: " + self.__save_directory)

    def __set_reference_data_data_frame(self):
        self.__reference_data_data_frame = get_file_as_data_frame(self.__template_file_name, 'ReferenceData')
        self.__reference_data_data_frame = self.__reference_data_data_frame.fillna(EMPTY_STRING)

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
                     wraplength=WRAPLENGHT)
    
    @staticmethod
    def __open_excel_file_via_dialog():
        return filedialog.askopenfilename(initialdir="/",
                                          title="Select a File",
                                          filetypes=(("Excel files",
                                                      "*.xls*"),))

    @staticmethod
    def __set_dropdown_with_options(dropdown_element, dropdown_var, options):
        options = filter(lambda cell: cell != EMPTY_STRING, options)
        dropdown_element.configure(state='normal')
        menu = dropdown_element['menu']
        menu.delete(0, 'end')
        for option in options:
            menu.add_command(label=option, command=lambda o=option: dropdown_var.set(o))