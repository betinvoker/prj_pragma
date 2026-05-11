from django.db import models
from django.contrib.auth.models import User


class Client(models.Model):
    name = models.CharField(max_length=255, unique=True)
    last_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Фамилия")
    first_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Имя")
    patronymic = models.CharField(max_length=100, blank=True, null=True, verbose_name="Отчество")
    company = models.CharField(max_length=255, blank=True, null=True, verbose_name="Название компании")
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    address = models.CharField(max_length=512, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class DocumentType(models.TextChoices):
    INVOICE = "INV", "Счет-фактура"
    CONTRACT = "CTR", "Договор"
    AGREEMENT = "AGR", "Соглашение"


class CatalogItem(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='catalog/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_CHOICES = [
        ("NEW", "Новый"),
        ("PROCESSING", "В обработке"),
        ("COMPLETED", "Завершено"),
        ("CANCELLED", "Отменено"),
    ]
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="orders")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="NEW")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    managed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders_managed")

    def __str__(self):
        return f"Order #{self.id} for {self.client.name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    item = models.ForeignKey(CatalogItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.item.name}"


class Document(models.Model):
    title = models.CharField(max_length=255)
    doc_type = models.CharField(max_length=3, choices=DocumentType.choices, default=DocumentType.INVOICE)
    content = models.TextField(blank=True, null=True)
    version = models.PositiveIntegerField(default=1)
    file = models.FileField(upload_to='documents/', null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="documents_created")
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, related_name="documents")
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name="documents")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} (v{self.version})"


class Consultation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="consultations")
    question = models.TextField()
    answer = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Consultation #{self.id} by {self.user.username}"