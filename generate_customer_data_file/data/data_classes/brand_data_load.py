from generate_customer_data_file.data.data_classes.data_load import DataLoad


class GenericBrandDataLoad(DataLoad):
    def __init__(self, window, data_load) -> None:
        super().__init__(window, data_load)
        self.admin_email = self._create_text_input()
        self.name = self._create_text_input()
        self.description = self._create_text_input()
        self.customer_id = self._create_text_input()
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
        self.expiration_date = self._create_text_input()


class AGNDataLoad(GenericBrandDataLoad):
    _FILE_NAME = 'AGN_Retail_Customers'

    def __init__(self, window, data_load) -> None:
        super().__init__(window, data_load)


class ATIDataLoad(GenericBrandDataLoad):
    _FILE_NAME = 'ATI_Retail_Customers'

    def __init__(self, window, data_load) -> None:
        super().__init__(window, data_load)


class A1800DataLoad(GenericBrandDataLoad):
    _FILE_NAME = '1800_Retail_Customers'

    def __init__(self, window, data_load) -> None:
        super().__init__(window, data_load)
