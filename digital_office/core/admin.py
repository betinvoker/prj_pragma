from django.contrib import admin
from .models import Client, Document, CatalogItem, Order, OrderItem, Consultation


class ClientAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "phone", "address", "created_at")
    search_fields = ("name", "email", "phone")
    list_filter = ("created_at",)


class CatalogItemAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price", "stock")
    search_fields = ("name",)
    list_filter = ("stock",)


class DocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "doc_type", "client", "created_at")
    search_fields = ("title", "doc_type", "client__name")
    list_filter = ("doc_type", "created_at")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "client", "status", "total_amount", "created_at")
    inlines = [OrderItemInline]
    search_fields = ("client__name",)
    list_filter = ("status", "created_at")


class ConsultationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "question", "answer", "created_at")
    search_fields = ("user__username", "question", "answer")


admin.site.register(Client, ClientAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(CatalogItem, CatalogItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(Consultation, ConsultationAdmin)

# Admin UI tweaks
admin.site.site_header = "Digital Office Admin"
admin.site.site_title = "Digital Office Admin Portal"
admin.site.index_title = "Добро пожаловать в административную панель"
