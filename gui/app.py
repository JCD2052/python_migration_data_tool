import sys
from datetime import datetime
from threading import Thread
from tkinter import filedialog, Tk, Button, Label


class App:
    def __init__(self):
        self.__window_background = 'white'
        self.__window_geometry = '800x330'
        self.__window_title = 'Data Migration Tool'
        self.__window = Tk()
        self.__select_template_file_label = Label(self.__window,
                                                  text="Select Excel file with blank template:",
                                                  width=80, height=2,
                                                  fg="blue", background='white')

        self.__select_template_file_button = Button(self.__window,
                                                    text="Select File",
                                                    command=self.__select_template_file)

        self.__select_product_data_file_label = Label(self.__window,
                                                      text="Select Excel file with product data:",
                                                      width=80, height=2,
                                                      fg="blue")

        self.__select_product_data_file_button = Button(self.__window,
                                                        text="Select File",
                                                        command=self.__select_product_data_file)

        self.__select_mirakl_product_data_file_label = Label(self.__window,
                                                             text="Select Excel file with Mirakl data:",
                                                             width=80, height=2,
                                                             fg="blue")

        self.__select_mirakl_product_data_file_button = Button(self.__window,
                                                               text="Select File",
                                                               command=self.__select_mirakl_data_file)

        self.__browse_save_directory_label = Label(self.__window,
                                                   text="Select a folder to save the file:",
                                                   width=80, height=2,
                                                   fg="blue")

        self.__browse_save_directory_button = Button(self.__window,
                                                     text="Select Directory",
                                                     command=self.__select_save_directory)

        self.__exit_button = Button(self.__window,
                                    text="Exit",
                                    command=sys.exit)

        self.__submit_button = Button(self.__window,
                                      text="Submit",
                                      command=self.__thread_submit)

        self.__status_label = Label(self.__window,
                                    text="",
                                    width=80, height=1,
                                    fg="blue")

        self.__template_file_name = ''
        self.__product_data_file_name = ''
        self.__mirakl_data_file_name = ''
        self.__save_directory = ''

    def run(self):
        self.__configure_app()
        self.__configure_grid()
        self.__window.mainloop()

    def __configure_grid(self):
        self.__select_template_file_label.grid(column=1, row=1)
        self.__select_template_file_button.grid(column=2, row=1)
        self.__select_product_data_file_label.grid(column=1, row=2)
        self.__select_product_data_file_button.grid(column=2, row=2)
        self.__select_mirakl_product_data_file_label.grid(column=1, row=3)
        self.__select_mirakl_product_data_file_button.grid(column=2, row=3)
        self.__browse_save_directory_label.grid(column=1, row=4)
        self.__browse_save_directory_button.grid(column=2, row=4)
        self.__submit_button.grid(column=1, row=11)
        self.__exit_button.grid(column=1, row=12)
        self.__status_label.grid(column=1, row=14)

    def __configure_app(self):
        self.__window.title(self.__window_title)
        self.__window.geometry(self.__window_geometry)
        self.__window.config(background=self.__window_background)

    def __thread_submit(self):
        return Thread(target=self.__submit, daemon=True).start()

    def __submit(self):
        try:
            current_time = App.__get_current_time_as_string()
            path = f"{self.__save_directory}/{current_time}"
            self.__status_label.configure(text=f"Done. The file has been saved to {path}", fg='blue')
        except Exception as e:
            self.__status_label.configure(text=f"ERROR. SOMETHING WENT WRONG {str(e)}", fg='red')

    def __select_template_file(self):
        self.__template_file_name = filedialog.askopenfilename(initialdir="/",
                                                               title="Select a File",
                                                               filetypes=(("Excel files",
                                                                           "*.xls*"),))
        self.__select_template_file_label.configure(
            text="Selected File with valid brands: " + self.__template_file_name)

    def __select_product_data_file(self):
        self.__product_data_file_name = filedialog.askopenfilename(initialdir="/",
                                                                   title="Select a File",
                                                                   filetypes=(("Excel files",
                                                                               "*.xls*"),))
        self.__select_product_data_file_label.configure(
            text="Selected Data File: " + self.__product_data_file_name)

    def __select_mirakl_data_file(self):
        self.__mirakl_data_file_name = filedialog.askopenfilename(initialdir="/",
                                                                  title="Select a File",
                                                                  filetypes=(("Excel files",
                                                                              "*.xls*"),))
        self.__select_mirakl_product_data_file_label.configure(
            text="Selected Data File: " + self.__mirakl_data_file_name)

    def __select_save_directory(self):
        self.__save_directory = filedialog.askdirectory()
        self.__browse_save_directory_label.configure(
            text="Selected Directory to save an output file: " + self.__save_directory)

    @staticmethod
    def __get_current_time_as_string():
        now = datetime.now()
        return now.strftime("%m_%d_%Y_%H_%M_%S")
