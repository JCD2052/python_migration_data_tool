import pandas as pd
from category_normalization.validators.validators import *

SPACE_STRING = ' '
sku_column_name = "MPSku"
df = pd.read_excel("C:\\Users\\proje\\Downloads\\SKU-Mapping-Final-Publication-20230720.xlsx")
df = df.fillna('')
level_categories_columns = list(filter(lambda x: str(x).lower().startswith('l'), df.columns))
unique_table_values = list(
    itertools.chain(*[list(filter(lambda x: bool(x), df[c].unique())) for c in level_categories_columns]))

errors = dict()
validators = [LowerAndValidator(),
              SpecialCharactersValidator(),
              ExtraSpacesValidator(),
              NonBreakingSpaceValidator(),
              SpellCheckValidator(),
              AlmostSameWordValidator(unique_table_values),
              DuplicatesInColumnValidator({col: v for col in level_categories_columns for v in df[col].unique()})]

for column in level_categories_columns:
    for value in filter(lambda x: str(x), df[column].unique()):
        res = [validator for validator in validators if validator.validate(value)]
        res.sort(key=lambda x: x.get_priority())
        if res:
            errors.update({value: res[0].get_background_color()})

for value in df[df[sku_column_name].duplicated() == True][sku_column_name].unique():
    if SkuDuplicateValidator().validate(value):
        errors.update({value: SkuDuplicateValidator.get_background_color()})

styled = df.style.applymap(lambda x: errors.get(x, None))
styled.to_excel(
    'C:\\Users\\proje\\PycharmProjects\\python_migration_data_tool\\category_normalization\\test.xlsx',
    engine='openpyxl')