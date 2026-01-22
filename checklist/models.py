from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


class Client(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cpf = models.CharField(max_length=30,null=True)
    cnpj = models.CharField(max_length=30,null=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=False)
    phone = models.CharField(max_length=20)
    insert_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Employee(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cpf = models.CharField(max_length=30)
    phone = models.CharField(max_length=20)
    position = models.CharField(max_length=100)
    insert_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.first_name
    

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
    orimento = models.CharField(max_length=100, null=True, blank=True)
    model = models.CharField(max_length=100, null=True, blank=True) 
    date_in = models.DateTimeField(null=True, blank=True)
    date_out = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES_ORDER, default="1")
    service = models.CharField(max_length=2000, null=True, blank=True)
    signature = models.ImageField(upload_to='imageFile/imgSignature/', blank=True,null=True)
    insert_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.operation_code)
    
    

STATUS_CHOICES_CHECKLIST= [
    ("1", "BOM"),
    ("2", "RUIM"),
    ("3", "Entrega"),
]
class Checklist(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    work_order = models.ForeignKey(WorkOrder,on_delete=models.CASCADE,related_name="checklists")    
    employee = models.ForeignKey(Employee,on_delete=models.CASCADE,related_name="checklists")    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES_CHECKLIST)
    picture = models.ImageField(upload_to='imageFile/imgChecklist/', blank=True,null=True)
    insert_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    
STATUS_CHOICES_CHECKLISTITEM = [
    (0, "False"),
    (1, "True"),
]
class ChecklistItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    status = models.IntegerField(choices=STATUS_CHOICES_ORDER, default=1)
    insert_date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name