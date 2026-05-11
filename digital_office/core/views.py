from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import Group, User

from django.db import models

from .forms import ClientForm, CatalogItemForm, DocumentForm
from .models import Client, CatalogItem, Order, OrderItem, Document, Consultation
from django.http import HttpResponse
from django.http import FileResponse
import os


def is_client(user):
    return user.is_authenticated and user.groups.filter(name="client").exists()


def is_manager(user):
    return user.is_authenticated and (
        user.groups.filter(name="manager").exists() or user.is_staff or user.is_superuser
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    return Response({"status": "ok"})


def web_home(request):
    # Simple web dashboard: list and create clients and catalog items
    if request.method == "POST":
        form_type = request.POST.get("form_type")
        if form_type == "client":
            client_form = ClientForm(request.POST)
            if client_form.is_valid():
                client_form.save()
                return redirect("web_home")
        elif form_type == "catalog":
            catalog_form = CatalogItemForm(request.POST)
            if catalog_form.is_valid():
                catalog_form.save()
                return redirect("web_home")
    else:
        client_form = ClientForm()
        catalog_form = CatalogItemForm()

    clients = Client.objects.all()
    catalogs = CatalogItem.objects.all()
    return render(
        request,
        "web/home.html",
        {
            "clients": clients,
            "catalogs": catalogs,
            "form_client": client_form,
            "form_catalog": catalog_form,
        },
    )


@login_required
def client_dashboard(request):
    if not is_client(request.user):
        return redirect("manager_dashboard") if is_manager(request.user) else redirect("admin:index")
    client, _ = Client.objects.get_or_create(name=request.user.username, defaults={"email": request.user.email})
    cart = request.session.get("cart", {})
    catalog = CatalogItem.objects.all()
    orders = Order.objects.filter(client=client).order_by("-created_at")
    documents = Document.objects.filter(client=client)
    return render(
        request,
        "portal/client/dashboard.html",
        {
            "catalog": catalog,
            "cart": cart,
            "orders": orders,
            "documents": documents,
            "client": client,
        },
    )


@login_required
def client_item_detail(request, item_id):
    if not is_client(request.user):
        return redirect("manager_dashboard") if is_manager(request.user) else redirect("admin:index")
    item = get_object_or_404(CatalogItem, id=item_id)
    return render(request, "portal/client/item_detail.html", {"item": item})


@login_required
def manager_dashboard(request):
    if not is_manager(request.user):
        return redirect("client_dashboard")
    catalog = CatalogItem.objects.all()
    return render(request, "portal/manager/dashboard.html", {"catalog": catalog})


@login_required
def manager_profile(request):
    from .forms import ClientProfileForm
    if not is_manager(request.user):
        return redirect("manager_dashboard")
    client, _ = Client.objects.get_or_create(name=request.user.username, defaults={"email": request.user.email})
    if request.method == "POST":
        form = ClientProfileForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            return redirect("manager_dashboard")
    else:
        form = ClientProfileForm(instance=client)
    return render(request, "portal/manager/profile.html", {"form": form})


@login_required
def cart_add(request):
    if not is_client(request.user):
        return redirect("client_dashboard")
    if request.method == "POST":
        item_id = request.POST.get("item_id")
        qty = int(request.POST.get("qty", 1))
        if not item_id:
            return redirect("client_dashboard")
        cart = request.session.get("cart", {})
        cart[item_id] = cart.get(item_id, 0) + qty
        request.session["cart"] = cart
    return redirect("client_dashboard")


@login_required
def cart_view(request):
    if not is_client(request.user):
        return redirect("client_dashboard")
    cart = request.session.get("cart", {})
    items = []
    total = 0
    for item_id, qty in cart.items():
        item = CatalogItem.objects.filter(id=item_id).first()
        if item:
            items.append({"item": item, "qty": qty, "line": item.price * qty, "id": item.id})
            total += item.price * qty
    return render(request, "portal/client/cart.html", {"cart_items": items, "total": total})


@login_required
def cart_update(request):
    if not is_client(request.user):
        return redirect("client_dashboard")
    if request.method == "POST":
        item_id = request.POST.get("item_id")
        qty = int(request.POST.get("qty", 1))
        cart = request.session.get("cart", {})
        if item_id in cart:
            if qty > 0:
                cart[item_id] = qty
            else:
                del cart[item_id]
            request.session["cart"] = cart
    return redirect("cart_view")


@login_required
def cart_remove(request):
    if not is_client(request.user):
        return redirect("client_dashboard")
    if request.method == "POST":
        item_id = request.POST.get("item_id")
        cart = request.session.get("cart", {})
        if item_id in cart:
            del cart[item_id]
            request.session["cart"] = cart
    return redirect("cart_view")


@login_required
def checkout(request):
    if not is_client(request.user):
        return redirect("client_dashboard")
    cart = request.session.get("cart", {})
    if not cart:
        return redirect("client_dashboard")
    client, _ = Client.objects.get_or_create(name=request.user.username, defaults={"email": request.user.email})
    order = Order.objects.create(client=client, status="NEW", total_amount=0)
    total = 0
    for item_id, qty in cart.items():
        item = CatalogItem.objects.filter(id=item_id).first()
        if item:
            OrderItem.objects.create(order=order, item=item, quantity=qty, price=item.price)
            item.stock = max(0, item.stock - qty)
            item.save()
            total += item.price * qty
    order.total_amount = total
    order.save()
    request.session["cart"] = {}
    return redirect("client_orders")


@login_required
def client_orders(request):
    if not is_client(request.user):
        return redirect("client_dashboard")
    client, _ = Client.objects.get_or_create(name=request.user.username, defaults={"email": request.user.email})
    orders = Order.objects.filter(client=client).prefetch_related('items', 'items__item', 'documents').order_by("-created_at")
    return render(request, "portal/client/orders.html", {"orders": orders})


@login_required
def client_documents(request):
    if not is_client(request.user):
        return redirect("client_dashboard")
    client, _ = Client.objects.get_or_create(name=request.user.username, defaults={"email": request.user.email})
    documents = Document.objects.filter(client=client).select_related('order')
    
    search_query = request.GET.get('search', '')
    if search_query:
        if search_query.isdigit():
            documents = documents.filter(order__id=search_query)
        else:
            documents = documents.filter(title__icontains=search_query)
    
    return render(request, "portal/client/documents.html", {"documents": documents, "search": search_query})


@login_required
def client_ai(request):
    if not (is_client(request.user) or is_manager(request.user)):
        return redirect("client_dashboard")
    if request.method == "POST":
        question = request.POST.get("question")
        answer = f"AI ответ на ваш вопрос: '{question}' (заглушка)"
        Consultation.objects.create(user=request.user, question=question, answer=answer)
        return redirect("client_ai")
    consultations = Consultation.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "portal/client/ai.html", {"consultations": consultations})


@login_required
def client_profile(request):
    from .forms import ClientSignupForm  # reuse simple form for editing if needed
    from .forms import ClientSignupForm as ProfileForm  # alias for clarity
    # We reuse Client model for profile data; ensure a Client exists for the user
    client, _ = Client.objects.get_or_create(name=request.user.username, defaults={"email": request.user.email})
    from .forms import ClientForm as ClientEditForm  # simple edit form
    form = ClientEditForm(instance=client)
    if request.method == "POST":
        form = ClientEditForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            return redirect("client_dashboard")
    return render(request, "portal/client/profile.html", {"form": form})


@login_required
def manager_catalog(request):
    if not is_manager(request.user):
        return redirect("client_dashboard")
    items = CatalogItem.objects.all()
    form = CatalogItemForm()
    if request.method == "POST":
        form = CatalogItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("manager_catalog")
    return render(request, "portal/manager/catalog.html", {"items": items, "form": form})


@login_required
def manager_catalog_add(request):
    if not is_manager(request.user):
        return redirect("client_dashboard")
    if request.method == "POST":
        form = CatalogItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("manager_catalog")
    else:
        form = CatalogItemForm()
    return render(request, "portal/manager/catalog_add.html", {"form": form})


@login_required
def manager_item_detail(request, item_id):
    if not is_manager(request.user):
        return redirect("manager_dashboard")
    item = get_object_or_404(CatalogItem, id=item_id)
    return render(request, "portal/manager/item_detail.html", {"item": item})


@login_required
def manager_orders(request):
    if not is_manager(request.user):
        return redirect("client_dashboard")
    orders = Order.objects.all().prefetch_related('items', 'items__item', 'documents', 'client').order_by("-created_at")
    
    search_query = request.GET.get("search", "")
    if search_query:
        if search_query.startswith('#'):
            order_id = search_query[1:]
            if order_id.isdigit():
                orders = orders.filter(id=order_id)
        elif search_query.isdigit():
            orders = orders.filter(id=search_query)
    
    if request.method == "POST":
        order_id = request.POST.get("order_id")
        new_status = request.POST.get("status")
        if order_id and new_status:
            order = Order.objects.filter(id=order_id).first()
            if order:
                order.status = new_status
                order.managed_by = request.user
                order.save()
                return redirect("manager_orders")
    return render(request, "portal/manager/orders.html", {"orders": orders, "search": search_query})


@login_required
def manager_order_detail(request, order_id):
    if not is_manager(request.user):
        return redirect("client_dashboard")
    order = get_object_or_404(Order.objects.prefetch_related('items__item', 'documents', 'client'), id=order_id)
    return render(request, "portal/manager/order_detail.html", {"order": order})


@login_required
def manager_users(request):
    if not is_manager(request.user):
        return redirect("client_dashboard")
    client_users = User.objects.filter(groups__name="client").values_list("username", flat=True)
    clients = Client.objects.filter(name__in=client_users).order_by("-created_at")
    search_query = request.GET.get("q", "")
    if search_query:
        clients = clients.filter(
            models.Q(id__icontains=search_query) |
            models.Q(first_name__icontains=search_query) |
            models.Q(last_name__icontains=search_query) |
            models.Q(patronymic__icontains=search_query) |
            models.Q(company__icontains=search_query) |
            models.Q(phone__icontains=search_query)
        )
    return render(request, "portal/manager/users.html", {"clients": clients, "q": search_query})


@login_required
def manager_client_detail(request, client_id):
    if not is_manager(request.user):
        return redirect("client_dashboard")
    client = get_object_or_404(Client, id=client_id)
    orders = Order.objects.filter(client=client).select_related("managed_by").prefetch_related("items__item").order_by("-created_at")
    return render(request, "portal/manager/client_detail.html", {"client": client, "orders": orders})


@login_required
def manager_documents(request):
    if not is_manager(request.user):
        return redirect("client_dashboard")
    documents = Document.objects.all().select_related('client', 'order')
    clients = Client.objects.all()
    orders = Order.objects.select_related('client').all()
    
    search_query = request.GET.get('search', '')
    if search_query:
        if search_query.startswith('#'):
            order_id = search_query[1:]
            if order_id.isdigit():
                documents = documents.filter(order__id=order_id)
        elif search_query.isdigit():
            documents = documents.filter(id=search_query) | documents.filter(order__id=search_query)
        else:
            documents = documents.filter(title__icontains=search_query) | documents.filter(client__name__icontains=search_query)
    
    form = DocumentForm()
    return render(request, "portal/manager/documents.html", {
        "documents": documents, 
        "form": form, 
        "search": search_query,
        "clients": clients,
        "orders": orders
    })


@login_required
def document_upload(request):
    if not is_manager(request.user):
        return redirect("manager_dashboard")
    if request.method == "POST":
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("manager_documents")
    else:
        form = DocumentForm()
    return render(request, "portal/manager/upload_document.html", {"form": form})


def client_signup(request):
    from .forms import ClientSignupForm
    if request.method == "POST":
        form = ClientSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            user_group, _ = Group.objects.get_or_create(name="client")
            user.groups.add(user_group)
            from .models import Client as ClientModel
            ClientModel.objects.create(name=user.username, email=user.email)
            login(request, user)
            return redirect("client_dashboard")
    else:
        form = ClientSignupForm()
    return render(request, "portal/client/signup.html", {"form": form})


def document_download(request, doc_id):
    doc = Document.objects.filter(id=doc_id).first()
    if not doc:
        return redirect("web_home")
    # Access control: managers can download any, clients only their documents
    if not (is_manager(request.user) or (request.user.is_authenticated and doc.client and doc.client.name == request.user.username)):
        return redirect("web_home")
    if doc.file:
        # Serve the uploaded file if available
        file_path = doc.file.path
        response = FileResponse(open(file_path, "rb"), as_attachment=True, filename=os.path.basename(doc.file.name))
        if doc.file.name.lower().endswith(".pdf"):
            response["Content-Type"] = "application/pdf"
        else:
            response["Content-Type"] = "application/octet-stream"
        return response
    # Fallback to text content
    content = (doc.content or "").encode("utf-8")
    response = HttpResponse(content, content_type="text/plain; charset=utf-8")
    filename = f"{doc.title}.txt"
    response["Content-Disposition"] = f"attachment; filename=\"{filename}\""
    return response


@login_required
def manager_analytics(request):
    if not is_manager(request.user):
        return redirect("client_dashboard")
    
    total_orders = Order.objects.count()
    avg_check = Order.objects.aggregate(avg=models.Avg('total_amount'))['avg'] or 0
    
    top_by_orders = Client.objects.annotate(
        order_count=models.Count('orders')
    ).filter(order_count__gt=0).order_by('-order_count')[:10]
    
    top_by_avg_check = Client.objects.annotate(
        avg_order=models.Avg('orders__total_amount'),
        order_count=models.Count('orders')
    ).filter(order_count__gt=0).order_by('-avg_order')[:10]
    
    data = {
        "clients": Client.objects.count(),
        "catalog_items": CatalogItem.objects.count(),
        "orders": total_orders,
        "documents": Document.objects.count(),
        "avg_check": avg_check,
        "top_by_orders": top_by_orders,
        "top_by_avg_check": top_by_avg_check,
    }
    return render(request, "portal/manager/analytics.html", {"data": data})
