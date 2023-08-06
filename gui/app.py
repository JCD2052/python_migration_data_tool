import re
import sys
from datetime import datetime
from threading import Thread
from tkinter import filedialog, Tk, Button, Label

import pandas as pd

from frame.read_excel import ExcelUtils


class App:
    def __init__(self):
        self.window_background = 'white'
        self.window_geometry = '800x330'
        self.window_title = 'Parser'
        self.window = Tk()
        self.browse_valid_brands_file_label = Label(self.window,
                                                    text="Select excel file with correct brand names:",
                                                    width=80, height=2,
                                                    fg="blue")

        self.browse_valid_brands_file_button = Button(self.window,
                                                      text="Browse File",
                                                      command=self.__browse_valid_brands_data_file)

        self.browse_data_file_label = Label(self.window,
                                            text="Select excel file data",
                                            width=80, height=2,
                                            fg="blue")

        self.browse_data_file_button = Button(self.window,
                                              text="Browse File",
                                              command=self.__browse_data_file)

        self.browse_save_directory_label = Label(self.window,
                                                 text="Select a folder to save the file:",
                                                 width=80, height=2,
                                                 fg="blue")

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
                                  width=80, height=1,
                                  fg="blue")

        self.valid_brands_file_name = ''
        self.data_file_name = ''
        self.save_directory = ''

    def run(self):
        self.__configure_app()
        self.__configure_grid()
        self.window.mainloop()

    def __configure_grid(self):
        self.browse_valid_brands_file_label.grid(column=1, row=1)
        self.browse_valid_brands_file_button.grid(column=2, row=1)
        self.browse_data_file_label.grid(column=1, row=2)
        self.browse_data_file_button.grid(column=2, row=2)
        self.browse_save_directory_label.grid(column=1, row=3)
        self.browse_save_directory_button.grid(column=2, row=3)
        self.submit_button.grid(column=1, row=11)
        self.exit_button.grid(column=1, row=12)
        self.status_label.grid(column=1, row=14)

    def __configure_app(self):
        self.window.title(self.window_title)
        self.window.geometry(self.window_geometry)
        self.window.config(background=self.window_background)

    def __thread_submit(self):
        return Thread(target=self.__submit, daemon=True).start()

    def __submit(self):
        try:
            valid_brands = ExcelUtils(self.valid_brands_file_name).get_file_as_data_frame("ReferenceData")['brand']
            df = ExcelUtils(self.data_file_name).get_file_as_data_frame()
            df.fillna('')

            results = []
            for index, brand in enumerate(df['brand'].to_numpy()):
                brand_string = str(brand)
                res = self.__find_string_in_lower_case_or_without_special_characters(brand_string, valid_brands)
                self.status_label.configure(text=f'{res} has been found for {brand_string} at index {index}', fg='blue')
                results.append(res)

            df['brand'] = pd.Series(results)
            current_time = App.__get_current_time_as_string()
            path = f"{self.save_directory}/{current_time}.xlsx"
            App.__save_excel_file(path, df)

            self.status_label.configure(text=f"Done. The file has been saved to {path}", fg='blue')
        except Exception as e:
            self.status_label.configure(text=f"ERROR. SOMETHING WENT WRONG {str(e)}", fg='red')

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

    @staticmethod
    def __save_excel_file(path, data_frame):
        data_frame.to_excel(path)

    @staticmethod
    def __get_current_time_as_string():
        now = datetime.now()
        return now.strftime("%m_%d_%Y_%H_%M_%S")

    @staticmethod
    def __find_string_in_lower_case_or_without_special_characters(origin_value, target_data):
        origin_value_in_lower_case = origin_value.lower()
        result = ''
        found_brand_with_lower_case = list(
            filter(lambda x: str(x).lower() == origin_value_in_lower_case or str(x).lower().startswith(
                origin_value_in_lower_case), target_data))
        if not found_brand_with_lower_case:
            found_brand_without_symbols = list(
                filter(lambda x: App.__get_string_without_special_characters(str(x).lower()) ==
                                 App.__get_string_without_special_characters(origin_value_in_lower_case),
                       target_data))
            try:
                result = found_brand_without_symbols[0]
            except IndexError:
                pass
        else:
            result = found_brand_with_lower_case[0]
        return result

    @staticmethod
    def __get_string_without_special_characters(value):
        return re.sub('\W+', '', value)
