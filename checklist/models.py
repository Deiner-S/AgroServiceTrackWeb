from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


class Address(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    street = models.CharField(max_length=255)
    number = models.CharField(max_length=20)
    complement = models.CharField(max_length=255, blank=True, default="")
    city = models.CharField(max_length=120)
    state = models.CharField(max_length=120)
    zip_code = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "addresses"

    def __str__(self):
        if self.complement:
            return (
                f"{self.street}, {self.number}, {self.complement} - "
                f"{self.city}/{self.state}"
            )
        return f"{self.street}, {self.number} - {self.city}/{self.state}"


class Client(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cpf = models.CharField(max_length=30,null=True)
    cnpj = models.CharField(max_length=30,null=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=False)
    phone = models.CharField(max_length=20)
    addresses = models.ManyToManyField(
        Address,
        through="ClientAddress",
        related_name="clients",
        blank=True,
    )
    insert_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
STATUS_CHOICES_POSITION = [
    ("0", "Diretor"),
    ("1", "Gerente"),
    ("2", "Administrativo"),
    ("3", "Técnico"),
]
class Employee(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cpf = models.CharField(max_length=30)
    phone = models.CharField(max_length=20)
    position = models.CharField(max_length=100, choices=STATUS_CHOICES_POSITION)
    addresses = models.ManyToManyField(
        Address,
        through="EmployeeAddress",
        related_name="employees",
        blank=True,
    )
    insert_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.first_name


class ClientAddress(models.Model):
    pk = models.CompositePrimaryKey("client", "address")
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="client_addresses",
    )
    address = models.ForeignKey(
        Address,
        on_delete=models.CASCADE,
        related_name="client_addresses",
    )

    class Meta:
        db_table = "client_addresses"
        indexes = [
            models.Index(fields=["client"], name="client_addr_client_idx"),
            models.Index(fields=["address"], name="client_addr_address_idx"),
        ]


class EmployeeAddress(models.Model):
    pk = models.CompositePrimaryKey("employee", "address")
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="employee_addresses",
    )
    address = models.ForeignKey(
        Address,
        on_delete=models.CASCADE,
        related_name="employee_addresses",
    )

    class Meta:
        db_table = "employee_addresses"
        indexes = [
            models.Index(fields=["employee"], name="employee_addr_emp_idx"),
            models.Index(fields=["address"], name="employee_addr_address_idx"),
        ]

    
STATUS_CHOICES_ORDER = [
    ("1", "Pendente"),
    ("2", "Andamento"),
    ("3", "Entrega"),
    ("4", "Finalizada")
]
class WorkOrder(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    operation_code = models.CharField(max_length=20, unique=True, blank=True)
    symptoms = models.CharField(max_length=1000)
    client = models.ForeignKey(Client,on_delete=models.CASCADE)
    chassi = models.CharField(max_length=100, null=True, blank=True)
    horimetro = models.CharField(max_length=100, null=True, blank=True)
    model = models.CharField(max_length=100, null=True, blank=True) 
    date_in = models.DateTimeField(null=True, blank=True)
    date_out = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES_ORDER, default="1")
    service = models.CharField(max_length=2000, null=True, blank=True)
    signature_in = models.ImageField(upload_to='imageFile/imgSignature/', blank=True, null=True)
    signature_out = models.ImageField(upload_to='imageFile/imgSignature/', blank=True, null=True)
    insert_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.operation_code)
    
STATUS_CHOICES_CHECKLISTITEM = [
    (0, "False"),
    (1, "True"),
]
class ChecklistItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    status = models.IntegerField(choices=STATUS_CHOICES_CHECKLISTITEM, default=1)
    insert_date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name
    

STATUS_CHOICES_CHECKLIST= [
    ("1", "BOM"),
    ("2", "Médio"),
    ("3", "Ruim"),
]
class Checklist(models.Model):
    id = models.UUIDField(primary_key=True, editable=True)
    work_order_fk = models.ForeignKey(WorkOrder,on_delete=models.CASCADE,related_name="checklists")    
    checklist_item_fk = models.ForeignKey(ChecklistItem,on_delete=models.CASCADE,related_name="executions")
    employee = models.ForeignKey(Employee,on_delete=models.CASCADE,related_name="checklists")    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES_CHECKLIST)
    image_in = models.ImageField(upload_to='imageFile/imgChecklist/', blank=True,null=True)
    image_out = models.ImageField(upload_to='imageFile/imgChecklist/', blank=True,null=True)
    insert_date = models.DateTimeField(auto_now_add=True)


    
    
