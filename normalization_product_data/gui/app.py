import sys
import traceback
from threading import Thread
from tkinter import filedialog, Tk, Button, Label
from utils.string_utils import *
from utils.excel_utils import *

import pandas as pd


class NormalizationTableApp:
    def __init__(self):
        self.window_background = 'white'
        self.window_geometry = '850x330'
        self.window_title = 'Parser'
        self.window = Tk()
        self.browse_valid_brands_file_label = Label(self.window,
                                                    text="Select excel file with correct brand reference data "
                                                         "and template:",
                                                    width=80, height=2,
                                                    fg="blue", background=self.window_background, wraplength=600)

        self.browse_valid_brands_file_button = Button(self.window,
                                                      text="Browse File",
                                                      command=self.__browse_valid_brands_data_file)

        self.browse_data_file_label = Label(self.window,
                                            text="Select excel file data",
                                            width=80, height=2,
                                            fg="blue", background=self.window_background, wraplength=600)

        self.browse_data_file_button = Button(self.window,
                                              text="Browse File",
                                              command=self.__browse_data_file)

        self.browse_save_directory_label = Label(self.window,
                                                 text="Select a folder to save the file:",
                                                 width=80, height=2,
                                                 fg="blue", background=self.window_background)

        self.browse_save_directory_button = Button(self.window,
                                                   text="Browse Directory ",
                                                   command=self.__browse_save_directory)

        self.exit_button = Button(self.window,
                                  text="Exit",
                                  command=sys.exit)

        self.submit_button = Button(self.window,
                                    text="Submit",
                                    command=self.__thread_submit)

        self.status_label = Label(self.window,
                                  text="",
                                  width=120, height=3, wraplength=600,
                                  fg="blue", background=self.window_background)

        self.valid_brands_file_name = ''
        self.data_file_name = ''
        self.save_directory = ''

    def run(self):
        self.__configure_app()
        self.__configure_grid()
        self.window.mainloop()

    def __configure_grid(self):
        self.browse_valid_brands_file_label.grid(column=1, row=1)
        self.browse_valid_brands_file_button.grid(column=1, row=2)
        self.browse_data_file_label.grid(column=1, row=3)
        self.browse_data_file_button.grid(column=1, row=4)
        self.browse_save_directory_label.grid(column=1, row=5)
        self.browse_save_directory_button.grid(column=1, row=6)
        self.submit_button.grid(column=1, row=11)
        self.exit_button.grid(column=1, row=12)
        self.status_label.grid(column=1, row=16)

    def __configure_app(self):
        self.window.title(self.window_title)
        self.window.geometry(self.window_geometry)
        self.window.config(background=self.window_background)

    def __thread_submit(self):
        return Thread(target=self.__submit, daemon=True).start()

    def __submit(self):
        try:
            self.status_label.configure(text='Reading data files....', fg='blue')
            template_df = get_file_as_data_frame(self.valid_brands_file_name, "Data")
            original_headers = template_df.columns
            template_df.columns = template_df.iloc[0]
            template_df = template_df.drop(template_df.index[0])
            columns_with_valid_order = template_df.columns.to_numpy()
            valid_brands = get_file_as_data_frame(self.valid_brands_file_name, "ReferenceData")['brand']
            valid_categories = get_file_as_data_frame(self.valid_brands_file_name, "ReferenceData")[
                'category']
            df = get_file_as_data_frame(self.data_file_name)
            df = df.fillna('')
            df = df.drop(filter(lambda column: 'mirakl-' in str(column), df.columns), axis=1)
            df.columns = map(lambda column: 'shop_sku' if 'sku' in column.lower() else column, df.columns)
            brands = []
            categories = []
            for index, row in df.iterrows():
                brand_string = str(row['brand'])
                category_string = str(row['category'])
                valid_brand = find_string_in_lower_case_or_without_special_characters(brand_string, valid_brands)
                valid_category = list(filter(
                    lambda x: category_string.lower() in get_string_without_special_characters(str(x).lower()),
                    valid_categories))
                valid_category = category_string if not valid_category else valid_category[0]
                self.status_label.configure(
                    text=f'{valid_brand} brand has been found for {brand_string} and {valid_category} category '
                         f'has been found for {category_string} at index {index}', fg='blue')
                brands.append(valid_brand)
                categories.append(valid_category)
            self.status_label.configure(text='Settings values to the columns....', fg='blue')
            df['brand'] = pd.Series(brands)
            df['category'] = pd.Series(categories)

            df = pd.merge(template_df, df, 'outer', on=list(df.columns))
            df = df[columns_with_valid_order]

            df.loc[-1] = df.columns  # adding a row
            df.index = df.index + 1  # shifting index
            df = df.sort_index()
            df.columns = original_headers
            self.status_label.configure(text='Saving data to file....')
            current_time = get_current_time_as_string()
            path = f"{self.save_directory}/{current_time}.xlsx"
            save_data_data_frame_as_excel_file_to_path(df, path)
            self.status_label.configure(text=f"Done. The file has been saved to {path}", fg='blue')
        except Exception:
            self.status_label.configure(f"ERROR. SOMETHING WENT WRONG: {traceback.format_exc()}")

    def __browse_valid_brands_data_file(self):
        self.valid_brands_file_name = filedialog.askopenfilename(initialdir="/",
                                                                 title="Select a File",
                                                                 filetypes=(("Excel files",
                                                                             "*.xls*"),))
        self.browse_valid_brands_file_label.configure(
            text="Selected File with valid brands: " + self.valid_brands_file_name)

    def __browse_data_file(self):
        self.data_file_name = filedialog.askopenfilename(initialdir="/",
                                                         title="Select a File",
                                                         filetypes=(("Excel files",
                                                                     "*.xls*"),))
        self.browse_data_file_label.configure(
            text="Selected Data File: " + self.data_file_name)

    def __browse_save_directory(self):
        self.save_directory = filedialog.askdirectory()
        self.browse_save_directory_label.configure(
            text="Selected Directory to save an output file: " + self.save_directory)
