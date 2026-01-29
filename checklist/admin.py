from django.contrib import admin
from .models import *


@admin.register(Client)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('id','cpf','cnpj', 'name', 'email','phone','insert_date')
    search_fields = ('id','cpf','cnpj', 'name', 'email','phone','insert_date')
    list_filter = ('insert_date',) 


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('id','first_name','last_name', 'cpf', 'phone','email','position','username','password')
    search_fields = ('id','first_name', 'email')
    list_filter = ('insert_date',)

@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    list_display = ('id','operation_code', 'chassi', 'client','orimento','model','date_in','date_out','service','status','signature','insert_date')
    search_fields = ('id','operation_code', 'chassi','client')
    list_filter = ('insert_date','client','chassi')

@admin.register(Checklist)
class ChecklistAdmin(admin.ModelAdmin):
    list_display = ('id', 'work_order_fk',"checklist_item_fk",'employee','status','image', 'insert_date')
    search_fields = ('work_order_fk',"checklist_item_fk", 'employee',"status")
    list_filter = ('insert_date','work_order_fk',"checklist_item_fk", 'employee',"status")

@admin.register(ChecklistItem)
class ChecklistItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'name','status','insert_date')
    search_fields = ('id', 'name','status','insert_date')
    list_filter = ('insert_date',)

