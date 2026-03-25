from checklist.models import ClientAddress
from checklist.repository.base_repository import BaseRepository


class ClientAddressRepository(BaseRepository):
    model = ClientAddress


client_address_repository = ClientAddressRepository()
