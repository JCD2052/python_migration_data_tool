from random_address import real_random_address


class RandomAddressGenerator:
    def __init__(self) -> None:
        address = real_random_address()
        self.address_line = address['address1']
        self.zip_code = address['postalCode']
        self.city = address['city']
        self.country = 'USA'
        self.state = f'{self.country}-{address["state"]}'
        self.address_email = 'test@gmail.com'
