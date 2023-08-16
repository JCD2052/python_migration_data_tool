from utils.data_address import RandomAddressGenerator
from generate_customer_data_file.data.data_classes.data_load import DataLoad


# Generic class for certain brand file type
class GenericBrandDataLoad(DataLoad):
    def __init__(self, window, data_load) -> None:
        super().__init__(window, data_load)
        self.admin_email = self._create_text_input()
        self.name = self._create_text_input()
        self.description = self._create_text_input()
        self.customer_id_require_7_digits = self._create_text_input()
        self.billing_address_street_name = self._create_text_input()
        self.billing_address_postal_code = self._create_text_input()
        self.billing_address_town = self._create_text_input()
        self.billing_address_country = self._create_text_input()
        self.billing_address_region = self._create_text_input()
        self.billing_address_email = self._create_text_input()
        self.shipping_address_street_name = self._create_text_input()
        self.shipping_address_postal_code = self._create_text_input()
        self.shipping_address_town = self._create_text_input()
        self.shipping_address_country = self._create_text_input()
        self.shipping_address_region = self._create_text_input()
        self.shipping_address_email = self._create_text_input()
        self.expiration_date = self._create_text_input()

    def generate_address(self) -> None:
        random_address = RandomAddressGenerator()
        self.billing_address_street_name.delete(0, 'end')
        self.billing_address_street_name.insert(0, random_address.address_line)
        self.billing_address_postal_code.delete(0, 'end')
        self.billing_address_postal_code.insert(0, random_address.zip_code)
        self.billing_address_town.delete(0, 'end')
        self.billing_address_town.insert(0, random_address.city)
        self.billing_address_country.delete(0, 'end')
        self.billing_address_country.insert(0, random_address.country)
        self.billing_address_region.delete(0, 'end')
        self.billing_address_region.insert(0, random_address.state)
        self.billing_address_email.delete(0, 'end')
        self.billing_address_email.insert(0, random_address.address_email)

        self.shipping_address_street_name.delete(0, 'end')
        self.shipping_address_street_name.insert(0, random_address.address_line)
        self.shipping_address_postal_code.delete(0, 'end')
        self.shipping_address_postal_code.insert(0, random_address.zip_code)
        self.shipping_address_town.delete(0, 'end')
        self.shipping_address_town.insert(0, random_address.city)
        self.shipping_address_country.delete(0, 'end')
        self.shipping_address_country.insert(0, random_address.country)
        self.shipping_address_region.delete(0, 'end')
        self.shipping_address_region.insert(0, random_address.state)
        self.shipping_address_email.delete(0, 'end')
        self.shipping_address_email.insert(0, random_address.address_email)


# Class for AGN Data type
class AGNDataLoad(GenericBrandDataLoad):
    _FILE_NAME = 'AGN_Retail_Customers'

    def __init__(self, window, data_load) -> None:
        super().__init__(window, data_load)


# Class for ATI Data type
class ATIDataLoad(GenericBrandDataLoad):
    _FILE_NAME = 'ATI_Retail_Customers'

    def __init__(self, window, data_load) -> None:
        super().__init__(window, data_load)


# Class for 1800 Data type
class A1800DataLoad(GenericBrandDataLoad):
    _FILE_NAME = '1800_Retail_Customers'

    def __init__(self, window, data_load) -> None:
        super().__init__(window, data_load)
