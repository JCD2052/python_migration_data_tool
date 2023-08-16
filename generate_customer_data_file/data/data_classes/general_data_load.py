from tkinter import ttk

from generate_customer_data_file.data.data_classes.data_load import DataLoad
from utils.data_type_constant import *

DEFAULT_ORG_ID = 'DBU'
DEFAULT_LIMIT = '750000.000'
TERMS_VALUES = ['DueOnReceipt', 'Net30', 'Net10', 'Net21']


class GeneralDataLoad(DataLoad):
    _FILE_NAME = 'MP_Customer'

    def __init__(self, window, data_load) -> None:
        super().__init__(window, data_load)
        self.brand_code = self._create_text_input()
        self.brand_code.insert(0, data_load.brand_code)
        self.customer_id = self._create_text_input()
        self.company_name = self._create_text_input()
        self.company_name.insert(0, data_load.company_name)
        self.description = self._create_text_input()
        self.reporting_organization_id = self._create_text_input()
        self.reporting_organization_id.insert(0, DEFAULT_ORG_ID)
        self.admin_email = self._create_text_input()
        self.name = self._create_text_input()
        self.billing_address_street_name = self._create_text_input()
        self.billing_address_postal_code = self._create_text_input()
        self.billing_address_town = self._create_text_input()
        self.billing_address_country = self._create_text_input()
        self.billing_address_region = self._create_text_input()
        self.billing_address_email = self._create_text_input()
        self.billing_address_title = self._create_text_input()
        self.shipping_address_street_name = self._create_text_input()
        self.shipping_address_postal_code = self._create_text_input()
        self.shipping_address_town = self._create_text_input()
        self.shipping_address_country = self._create_text_input()
        self.shipping_address_region = self._create_text_input()
        self.shipping_address_email = self._create_text_input()
        self.shipping_address_title = self._create_text_input()
        self.credit_limit = self._create_text_input()
        self.credit_limit.insert(0, DEFAULT_LIMIT)
        self.credit_balance = self._create_text_input()
        self.credit_balance.insert(0, DEFAULT_LIMIT)
        self.currency_id = self._create_text_input()
        self.currency_id.insert(0, 'USD')
        self.credit_terms = tkinter.ttk.Combobox(self.window, values=TERMS_VALUES)
        self.warehouse = self._create_text_input()
        self.warehouse.insert(0, data_load.warehouse_name)
        self.discount_price_group = self._create_text_input()
