import re
from datetime import datetime
from typing import List

EMPTY_STRING = ''


# Look in target_data list if origin value in lower case or without spec character matches with selected.
# Return an empty string if nothing found
def find_string_in_lower_case_or_without_special_characters(origin_value: str, target_data: List[str]) -> str:
    origin_value_in_lower_case = origin_value.lower()
    result = EMPTY_STRING
    found_brand_with_lower_case = list(
        filter(lambda x: str(x).lower() == origin_value_in_lower_case or str(x).lower().startswith(
            origin_value_in_lower_case), target_data))
    if not found_brand_with_lower_case:
        found_brand_without_symbols = list(
            filter(lambda value: get_string_without_special_characters(
                str(value).lower()) == get_string_without_special_characters(origin_value_in_lower_case),
                   target_data))
        try:
            result = found_brand_without_symbols[0]
        except IndexError:
            pass
    else:
        result = found_brand_with_lower_case[0]
    return result


# Remove all spec characters from target string
def get_string_without_special_characters(value: str) -> str:
    return re.sub('\\W+', '', value)


# Receive current time in string
def get_current_time_as_string() -> str:
    now = datetime.now()
    return now.strftime("%m_%d_%Y_%H_%M_%S")
