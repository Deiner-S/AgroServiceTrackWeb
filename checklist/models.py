from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


class Client(models.Model):
    cnpj = models.CharField(max_length=30)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=False)
    phone = models.CharField(max_length=20)
    insert_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Worker(AbstractUser):
    cpf = models.CharField(max_length=30, primary_key=True)
    phone = models.CharField(max_length=20)
    position = models.CharField(max_length=100)
    insert_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.first_name

class DataSheet(models.Model):
    code = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    operation_code = models.CharField(max_length=20, unique=True, blank=True)
    symptoms = models.CharField(max_length=1000)
    client = models.ForeignKey(Client,on_delete=models.CASCADE)
    chassi = models.CharField(max_length=100, null=True, blank=True)
    orimento = models.CharField(max_length=100, null=True, blank=True)
    model = models.CharField(max_length=100, null=True, blank=True) 
    date_in = models.DateTimeField(null=True, blank=True)
    date_out = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, null=True, blank=True)
    service = models.CharField(max_length=2000, null=True, blank=True)
    insert_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.operation_code:
            ultimo = DataSheet.objects.order_by('insert_date').last()
            proximo = 1 if not ultimo else int(ultimo.operation_code) + 1
            self.operation_code = f"{proximo:06d}"  # 000001, 000002...
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.operation_code)

    
    

class checklist(models.Model):
    name = models.CharField(max_length=100)
    datasheet = models.ForeignKey(DataSheet,on_delete=models.CASCADE,related_name="checklists")    
    worker = models.ForeignKey(Worker,on_delete=models.CASCADE,related_name="checklists")    
    status = models.CharField(max_length=10)
    picture = models.ImageField(upload_to='funcionarios/', blank=True,null=True)
    insert_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
