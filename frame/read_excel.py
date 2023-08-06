import pandas as pd


class ExcelUtils:
    __EXCEL_FILE_EXTENSION = 'xlsx'

    @staticmethod
    def get_file_as_data_frame(path, sheet_name=None):
        if sheet_name is None:
            return pd.read_excel(path)
        else:
            return pd.read_excel(path, sheet_name=sheet_name)

    @staticmethod
    def save_data_data_frame_as_excel_file_to_path(data_frame, path_to_save):
        data_frame.to_excel(f'{path_to_save}.xlsx', index=False)
