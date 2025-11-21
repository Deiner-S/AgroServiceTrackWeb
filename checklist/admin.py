from django.contrib import admin
from .models import *


@admin.register(Client)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('cnpj', 'name', 'email','phone','insert_date')
    search_fields = ('cnpj', 'name', 'email','phone','insert_date')
    list_filter = ('insert_date',) 


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('first_name','last_name', 'cpf', 'phone','email','position','username','password')
    search_fields = ('first_name', 'email')
    list_filter = ('insert_date',)

@admin.register(DataSheet)
class DataSheetAdmin(admin.ModelAdmin):
    list_display = ('code','operation_code', 'chassi', 'client','orimento','model','date_in','date_out','service','status','insert_date')
    search_fields = ('code','operation_code', 'chassi','client')
    list_filter = ('insert_date','client','chassi')

@admin.register(Checklist)
class ChecklistAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'datasheet','employee','status','picture', 'insert_date')
    search_fields = ('datasheet', 'employee',"status")
    list_filter = ('insert_date','datasheet', 'employee',"status")

