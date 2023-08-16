import random
from utils.addresses import addresses


# Get random address from addresses dict
def get_random_address():
    return random.choice(addresses.get('addresses'))


class RandomAddressGenerator:
    def __init__(self) -> None:
        address = get_random_address()
        self.address_line = address['address1']
        self.zip_code = address['postalCode']
        self.city = address['city']
        self.country = 'USA'
        self.state = f'{self.country}-{address["state"]}'
        self.address_email = 'test@gmail.com'
