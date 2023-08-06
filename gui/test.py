import numpy
import pandas as pd

SKU_TABLE_KEY = 'sku'

EMPTY_STRING = ''
MIRAKL_PRODUCT_POST_FIX = '_0001'
LEFT_SUFFIX = 'merge_left_suffix'
RIGHT_SUFFIX = 'merge_right_suffix'
SKU_POSTFIX = '_01'
CATEGORY = 'All Products'
PRODUCT_ID_TYPE = 'SHOP_SKU'
QUANTITY = '50000'

# read Excel file with products
product_df = pd.read_excel('C:\\Users\\proje\\Downloads\\Guniwheel-Products-Prod-8.1.xlsx')
# read Excel file with mirakl data
offer_df = pd.read_excel("C:\\Users\\proje\\Downloads\\Guniwheel-Offers-Prod-8.1.xlsx")
# remove mirakl postfix from sku column values
offer_df[SKU_TABLE_KEY] = pd.Series(
    map(lambda sku: str(sku).replace(MIRAKL_PRODUCT_POST_FIX, EMPTY_STRING), offer_df[SKU_TABLE_KEY].to_numpy()))
# read Excel file with template
template_df = pd.read_excel("C:\\Users\\proje\\Downloads\\Blank-products-and-offers-Form (1).xlsx")
# merge product data table to with template
data = pd.merge(template_df, product_df, how='right', on=list(product_df.columns))
# save original headers
original_headers = data.columns
data.columns = data.iloc[0]
data = data.drop(data.index[0])
# save secondary headers in right orders
columns_with_valid_order = data.columns.to_numpy()
# merge result table from previous merge with mirakl data table
data = pd.merge(data, offer_df, how='left', left_on='shop_sku', right_on=SKU_TABLE_KEY,
                suffixes=(LEFT_SUFFIX, RIGHT_SUFFIX))
# replace NAN values in result table to empty string
data = data.fillna(EMPTY_STRING)
# remove created columns after merge
cols = list(filter(lambda column: LEFT_SUFFIX not in str(column), data.columns))
data = data[cols]
data.columns = data.columns.str.replace(RIGHT_SUFFIX, EMPTY_STRING)
data = data[columns_with_valid_order]
# set entire 'product-id' column with values from 'sku' column
data['product-id'] = data[SKU_TABLE_KEY]
# add sku postfix to 'sku' column values
data[SKU_TABLE_KEY] = pd.Series(
    map(lambda sku: f'{str(sku)}{SKU_POSTFIX}' if str(sku) is not EMPTY_STRING else EMPTY_STRING,
        data[SKU_TABLE_KEY].to_numpy()))
# set entire column with certain value
data = data.assign(**{'category': CATEGORY})
data['product-id-type'] = numpy.where(data[SKU_TABLE_KEY] == EMPTY_STRING, EMPTY_STRING, PRODUCT_ID_TYPE)
data['quantity'] = numpy.where(data[SKU_TABLE_KEY] == EMPTY_STRING, EMPTY_STRING, QUANTITY)

# add back original header row
data.loc[-1] = data.columns  # adding a row
data.index = data.index + 1  # shifting index
data = data.sort_index()
data.columns = original_headers

# save result table to Excel file
data.to_excel("result.xlsx", index=False)
