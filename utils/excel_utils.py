import pandas as pd

__EXCEL_FILE_EXTENSION = 'xlsx'


# Read Excel file as DataFrame
def get_file_as_data_frame(path: str, sheet_name: str = None) -> pd.DataFrame:
    if sheet_name is None:
        return pd.read_excel(path, engine='openpyxl')
    else:
        return pd.read_excel(path, sheet_name=sheet_name, engine='openpyxl')


# Save a dataframe to selected path as .xlsx file
def save_data_data_frame_as_excel_file_to_path(data_frame: pd.DataFrame, path_to_save: str) -> None:
    data_frame.to_excel(f'{path_to_save}.{__EXCEL_FILE_EXTENSION}', index=False)
