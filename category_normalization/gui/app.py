import tkinter
import traceback
import subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Thread
from tkinter import Tk, Button, Label, filedialog

from utils.label_logger import LabelLogger
from utils.excel_utils import *
from utils.color_constants import *
from category_normalization.validators.validators import *
from category_normalization.data_manipulation.data_manipulation import DataManipulation

SPACE_STRING = ' '
sku_column_name = "MPSku"

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
            self.__status_label.info(f'Normalization of table {Path(self.__data_file_name).name}...')
            sheet_name = pd.ExcelFile(self.__data_file_name).sheet_names[0]
            self.__status_label.info(f'first sheet: {sheet_name}')
            df = get_file_as_data_frame(self.__data_file_name, sheet_name)
            df = df.fillna('')
            data_obj = DataManipulation(df)
            errors = dict()
            errors_df = []
            validators = [LowerAndValidator(),
                          SpecialCharactersValidator(),
                          ExtraSpacesValidator(),
                          NonBreakingSpaceValidator(),
                          # SpellCheckValidator(),
                          AlmostSameWordValidator(data_obj.get_unique_values_from_table()),
                          DuplicatesInColumnValidator(data_obj.get_column_almost_same_values()),
                          DuplicateWithWrongHierarchyValidator(data_obj.find_categories_with_wrong_hierarchy()),
                          CheckCategoryHierarchyValidator(data_obj.find_duplicated_categories_with_wrong_leveling())]

            for column in data_obj.category_columns:
                def check_value(category_value):
                    self.__status_label.info(f'Checking {category_value} in column {column}')
                    failed_validators = []
                    messages = []
                    for val in validators:
                        res = val.validate(category_value)
                        if res[0]:
                            failed_validators.append(val)
                            messages.append(res[1])
                    failed_validators.sort(key=lambda x: x.get_priority())
                    if failed_validators:
                        bg_color = failed_validators[0].get_background_color()
                        errors_df.append({"Value": category_value, "Reason": ". ".join(messages)})
                        errors.update({category_value: bg_color})

                values = list(filter(lambda x: str(x), df[column].unique()))
                with ThreadPoolExecutor(max_workers=8) as executor:
                    futures = [executor.submit(check_value, v) for v in values]
                    [call.result() for call in futures]

            if sku_column_name in df.columns:
                self.__status_label.info(f'Checking skus column for duplicates...')
                unique_sku_values = df[sku_column_name].unique()
                sku_duplicates = list(df[df[sku_column_name].duplicated() == True][sku_column_name].unique())
                sku_validators = [UpperMPInSkuValidator(),
                                  DuplicateInSkuValidator(sku_duplicates),
                                  ExtraSpacesValidator(),
                                  NonBreakingSpaceValidator(),
                                  AlmostSameWordValidator(unique_sku_values)]
                for value in filter(lambda x: str(x), unique_sku_values):
                    validator_message = []
                    results = []
                    for sku_validator in sku_validators:
                        result = sku_validator.validate(value)
                        if result[0]:
                            results.append(sku_validator)
                            validator_message.append(result[1])
                    results.sort(key=lambda x: x.get_priority())
                    if results:
                        color = results[0].get_background_color()
                        errors_df.append({"Value": value, "Reason": ". ".join(validator_message)})
                        errors.update({value: color})

            criteries_colored = dict()
            criteria_names = []
            validators.extend([DuplicateInSkuValidator(list()), UpperMPInSkuValidator()])
            for validator in sorted(validators, key=lambda x: x.get_priority()):
                priority_name = f"Priority {validator.get_priority()}. {validator.get_name()}"
                criteria_names.append({"Normalization criteries": priority_name})
                criteries_colored.update({priority_name: validator.get_background_color()})

            styled = df.style.applymap(lambda x: errors.get(x, None))
            new_file_path = Path(os.path.dirname(self.__data_file_name),
                                 f"{FILE_PREFIX}_{Path(self.__data_file_name).name}")
            with pd.ExcelWriter(new_file_path, engine='openpyxl') as writer:
                self.__status_label.info(f'Saving tabs.....')
                df.to_excel(writer, sheet_name=sheet_name, index=False, engine='openpyxl')
                styled.to_excel(writer, sheet_name="Validated", index=False, engine='openpyxl')
                pd.DataFrame(errors_df).style.applymap(lambda x: errors.get(x, None)).to_excel(writer,
                                                                                               sheet_name="Errors",
                                                                                               index=False,
                                                                                               engine='openpyxl')
                pd.DataFrame(criteria_names).style.applymap(lambda x: criteries_colored.get(x, None)).to_excel(writer,
                                                                                                               sheet_name="Criteries",
                                                                                                               index=False,
                                                                                                               engine='openpyxl')
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

    # Get save directory
    def __open_file_folder(self):
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        return subprocess.call([opener, os.path.abspath(os.path.dirname(self.__data_file_name))])

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
