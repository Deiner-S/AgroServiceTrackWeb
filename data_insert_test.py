from checklist.models import Client, Employee, DataSheet, Checklist
from django.utils import timezone
import uuid
 
# -------------------------
# CLIENTES
# -------------------------


c1 = Client.objects.create(
    cnpj="12.345.678/0001-90",
    name="Auto Mecânica Horizonte",
    email="contato@horizonte.com",
    phone="(11) 99999-1234"
)

c2 = Client.objects.create(
    cnpj="98.765.432/0001-11",
    name="Serviços Veiculares Estrela",
    email="contato@estrela.com",
    phone="(21) 98888-4321"
) 

# -------------------------
# FUNCIONÁRIOS
# -------------------------
w1 = Employee.objects.create(
    cpf="123.456.789-00",
    name="Carlos Mendes",
    phone="(11) 97777-1111",
    email="carlos.mendes@example.com",
    position="Mecânico"
)

w2 = Employee.objects.create(
    cpf="987.654.321-00",
    name="Juliana Rocha",
    phone="(11) 96666-2222",
    email="juliana.rocha@example.com",
    position="Supervisora"
)

# -------------------------
# DATASHEETS
# -------------------------
d1 = DataSheet.objects.create(
    code=uuid.uuid4(),
    chassi="9BWZZZ377VT004251",
    client=c1,
    orimento="Guarulhos",
    model="Volkswagen Polo 1.6",
    date_in=timezone.now() - timezone.timedelta(days=3),
    date_out=timezone.now() + timezone.timedelta(days=2),
    status="open",
    service="Troca de óleo, revisão geral do motor e alinhamento."
)

d2 = DataSheet.objects.create(
    code=uuid.uuid4(),
    chassi="3VWFE21JXFM000987",
    client=c2,
    orimento="São Paulo",
    model="Chevrolet Onix LT",
    date_in=timezone.now() - timezone.timedelta(days=1),
    date_out=timezone.now() + timezone.timedelta(days=4),
    status="open",
    service="Verificação elétrica completa e substituição da bateria."
)

# -------------------------
# CHECKLISTS
# -------------------------
# *Obs*: picture é obrigatório, então coloquei um caminho fictício.
# Ele só precisa existir no sistema de arquivos.

Checklist.objects.create(
    name="Revisão Inicial - Motor",
    datasheet=d1,
    worker=w1,
    status="ok",
    
)

Checklist.objects.create(
    name="Avaliação Geral - Suspensão",
    datasheet=d1,
    worker=w2,
    status="pendente",
    
)

Checklist.objects.create(
    name="Inspeção Elétrica",
    datasheet=d2,
    worker=w1,
    status="ok",
    
)
