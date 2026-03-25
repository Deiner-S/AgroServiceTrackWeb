from checklist.models import EmployeeAddress
from checklist.repository.base_repository import BaseRepository


class EmployeeAddressRepository(BaseRepository):
    model = EmployeeAddress


employee_address_repository = EmployeeAddressRepository()
