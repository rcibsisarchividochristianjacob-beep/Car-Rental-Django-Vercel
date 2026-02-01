from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib import auth
from car_dealer_portal.models import *
from customer_portal.models import *
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect    

from django.urls import reverse


from django.http import JsonResponse 
from .models import Vehicles


from django.contrib.auth import authenticate
from car_dealer_portal.models import CarDealer, Vehicles
# Create your views here.

from django.db.models import Sum, F
from django.db.models import Sum
from datetime import datetime
from datetime import date



















def admin_chat_hub(request):
    return render(request, 'admin_chat_hub.html')







def search_ajax(request):
    q = request.GET.get('q', '')
    results = []
    if q:
        cars = Vehicles.objects.filter(car_name__icontains=q)[:10]
        results = [{'car_name': car.car_name} for car in cars]
    return JsonResponse(results, safe=False)





def index(request):
    if not request.user.is_authenticated:
        return render(request, 'car_dealer/login.html')
    else:
        return render(request, 'car_dealer/home_page.html')

def login(request):
    return render(request, 'car_dealer/login.html')






def auth_view(request):
    # Kung naka-login na, diretso sa home_page
    if request.user.is_authenticated:
        return redirect('/car_dealer_portal/home_page/')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(request, username=username, password=password)

        try:
            car_dealer = CarDealer.objects.get(car_dealer=user)
        except CarDealer.DoesNotExist:
            car_dealer = None

        if user is not None and car_dealer is not None:
            auth.login(request, user)
            return redirect('/car_dealer_portal/home_page/')
        else:
            return render(request, 'car_dealer/admin_login_failed.html')

    # GET request, ipakita ang login form
    return render(request, 'car_dealer/login.html')








def logout_view(request):
    auth.logout(request)
    return render(request, 'car_dealer/login.html')

def register(request):
    return render(request, 'car_dealer/register.html')

def registration(request):
    username = request.POST['username']
    password = request.POST['password']
    mobile = request.POST['mobile']
    firstname = request.POST['firstname']
    lastname = request.POST['lastname']
    email = request.POST['email']
    city = request.POST['city']
    city = city.lower()
    pincode = request.POST['pincode']

    try:
        user = User.objects.create_user(username = username, password = password, email = email)
        user.first_name = firstname
        user.last_name = lastname
        user.save()
    except:
        return render(request, 'car_dealer/registration_error.html')
    try:
        area = Area.objects.get(city = city, pincode = pincode)
    except:
        area = None
    if area is not None:
        car_dealer = CarDealer(car_dealer = user, mobile = mobile, area=area)
    else:
        area = Area(city = city, pincode = pincode)
        area.save()
        area = Area.objects.get(city = city, pincode = pincode)
        car_dealer = CarDealer(car_dealer = user, mobile = mobile, area=area)
    car_dealer.save()
    return render(request, 'car_dealer/registered.html')







@login_required
def add_vehicle(request):
    if request.method == 'POST':
        car_name = request.POST['car_name']
        color = request.POST['color']
        cd = CarDealer.objects.get(car_dealer=request.user)
        city = request.POST['city'].lower()
        pincode = request.POST['pincode']
        description = request.POST['description']
        capacity = request.POST['capacity']
        price_per_day = request.POST['price_per_day']
        image = request.FILES.get('image')

        # Check or create area
        area, created = Area.objects.get_or_create(city=city, pincode=pincode)

        # Save vehicle with all fields (kasama image at price)
        car = Vehicles.objects.create(
            car_name=car_name,
            color=color,
            dealer=cd,
            area=area,
            description=description,
            capacity=capacity,
            price_per_day=price_per_day,
            image=image
        )

        # Redirect agad sa dashboard (home_page) para fresh list
        return HttpResponseRedirect('/car_dealer_portal/home_page/')

    # fallback
    return HttpResponseRedirect('/car_dealer_portal/home_page/')






@login_required
def manage_vehicles(request):
    username = request.user
    user = User.objects.get(username = username)
    car_dealer = CarDealer.objects.get(car_dealer = user)
    vehicle_list = []
    vehicles = Vehicles.objects.filter(dealer = car_dealer)
    for v in vehicles:
        vehicle_list.append(v)
    return render(request, 'car_dealer/manage.html', {'vehicle_list':vehicle_list})












@login_required
def order_list(request):
    username = request.user
    user = User.objects.get(username=username)
    car_dealer = CarDealer.objects.get(car_dealer=user)
    orders = Orders.objects.filter(car_dealer=car_dealer)
    
    today = date.today()
    orders_data = []

    for o in orders:
        if not o.is_complete:
            # Countdown Logic
            delta = o.return_date - today
            o.remaining_days = delta.days
            
            # Penalty Logic (Lalabas lang kung overdue)
            o.penalty = 0
            if o.remaining_days < 0:
                o.penalty = abs(o.remaining_days) * 1000 
            
            orders_data.append(o)
            
    # TAMA NA DAPAT ITO BASE SA SCREENSHOT MO:
    return render(request, 'car_dealer/order_list.html', {'order_list': orders_data})

@login_required
def complete(request):
    order_id = request.POST['id']
    order = Orders.objects.get(id = order_id)
    vehicle = order.vehicle
    order.is_complete = True
    order.save()
    vehicle.is_available = True
    vehicle.save()
    return HttpResponseRedirect('/car_dealer_portal/order_list/')


@login_required
def history(request):
    try:
        car_dealer = CarDealer.objects.get(car_dealer=request.user)
        
        # Kunin ang filter values mula sa dropdown
        month = request.GET.get('month')
        year = request.GET.get('year')

        # Filter completed orders
        completed_orders = Orders.objects.filter(car_dealer=car_dealer, is_complete=True)

        # Apply Month filter (if not "0"/All)
        if month and month != "0":
            completed_orders = completed_orders.filter(return_date__month=month)
            
        # Apply Year filter
        if year:
            completed_orders = completed_orders.filter(return_date__year=year)

        completed_orders = completed_orders.order_by('-id')

        # Re-compute income based on filtered results
        total_income = sum(float(order.rent) for order in completed_orders)
        
        # Para sa Year dropdown
        current_year = datetime.now().year
        years_list = range(current_year, current_year - 5, -1)

    except CarDealer.DoesNotExist:
        completed_orders = []
        total_income = 0
        years_list = [datetime.now().year]

    return render(request, 'car_dealer/history.html', {
        'wallet': total_income,
        'order_list': completed_orders,
        'years': years_list,
    })




@login_required
def delete_vehicle(request, vehicle_id):
    try:
        vehicle = Vehicles.objects.get(id=vehicle_id, dealer__car_dealer=request.user)
        # delete all related orders first
        Orders.objects.filter(vehicle=vehicle).delete()
        vehicle.delete()
        return HttpResponseRedirect('/car_dealer_portal/manage_vehicles/')
    except Vehicles.DoesNotExist:
        return HttpResponse("Vehicle not found or you don't have permission.", status=404)












@login_required
def home_page(request):
    user = request.user
    query = request.GET.get('q')  # optional search query

    try:
        # Kunin ang CarDealer object na naka-link sa user na naka-login
        car_dealer = CarDealer.objects.get(car_dealer=user)
        print("CarDealer found:", car_dealer)

        # Kunin lahat ng vehicles ng dealer na ito
        if query:
            vehicles = Vehicles.objects.filter(
                dealer=car_dealer,
                car_name__icontains=query
            ) | Vehicles.objects.filter(
                dealer=car_dealer,
                description__icontains=query
            )
        else:
            vehicles = Vehicles.objects.filter(dealer=car_dealer)

        found = vehicles.exists()

    except CarDealer.DoesNotExist:
        print("Walang CarDealer record para sa user na ito.")
        vehicles = Vehicles.objects.all()  # fallback: ipakita lahat ng vehicles
        found = False

    return render(request, 'car_dealer/home_page.html', {
        'vehicles': vehicles,
        'found': found
    })







@login_required
def edit_vehicle(request, vehicle_id):
    try:
        vehicle = Vehicles.objects.get(id=vehicle_id, dealer__car_dealer=request.user)
    except Vehicles.DoesNotExist:
        return HttpResponse("Vehicle not found or you don't have permission.", status=404)

    if request.method == 'POST':
        vehicle.car_name = request.POST['car_name']
        vehicle.color = request.POST['color']
        vehicle.description = request.POST['description']
        vehicle.capacity = request.POST['capacity']
        vehicle.price_per_day = request.POST['price_per_day']

        if request.FILES.get('image'):
            vehicle.image = request.FILES['image']

        vehicle.save()
        return redirect('/car_dealer_portal/home_page/')

    
    return render(request, 'car_dealer/edit_vehicle.html', {'vehicle': vehicle})









