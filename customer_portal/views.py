from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib import auth, messages
from customer_portal.models import *
from car_dealer_portal.models import *
from django.contrib.auth.decorators import login_required
from datetime import date


from car_dealer_portal.models import Vehicles
from .models import Orders


from django.shortcuts import render
from django.contrib.auth import authenticate, login as auth_login
from django.http import HttpResponseRedirect
from customer_portal.models import Customer

@login_required
def confirm(request):
    if request.method == "POST":
        # Kunin ang data mula sa form (Personal Rent Details)
        vehicle_name = request.POST.get("vehicle_name")
        customer_name = request.POST.get("customer_name")
        customer_address = request.POST.get("customer_address")
        rental_date = request.POST.get("rental_date")
        return_date = request.POST.get("return_date")
        description = request.POST.get("description")
        payment_method = request.POST.get("payment_method")
        payment_proof = request.FILES.get("payment_proof")

        try:
            total_days = int(request.POST.get("total_days") or 1)
        except ValueError:
            total_days = 1

        # Hanapin ang sasakyan
        try:
            vehicle = Vehicles.objects.get(car_name=vehicle_name)
        except Vehicles.DoesNotExist:
            return render(request, "customer/order_failed.html", {"message": "Vehicle not found."})

        if vehicle.is_available:
            # Compute total rent
            total_rent = float(vehicle.price_per_day) * total_days
            car_dealer = vehicle.dealer # Siguraduhin na 'car_dealer' ang field name sa Vehicles model mo

            # 🔹 SAVE TO DATABASE (Dito papasok ang personal details ni Christian Jacob)
            order = Orders.objects.create(
                user=request.user,
                car_dealer=car_dealer,
                vehicle=vehicle,
                customer_name=customer_name,
                customer_address=customer_address,
                rental_date=rental_date,
                return_date=return_date,
                description=description,
                payment_method=payment_method,
                payment_proof=payment_proof,
                rent=total_rent,
                days=total_days
            )

            # Update status ng dealer at kotse
            car_dealer.wallet += total_rent
            car_dealer.save()
            vehicle.is_available = False
            vehicle.save()

            # I-save ang last order ID sa session
            request.session['last_order_id'] = order.id

            return render(request, 'customer/confirmed.html', {'order': order})
        else:
            return render(request, 'customer/order_failed.html', {'message': "Sorry, this vehicle is no longer available."})

    # Para sa GET request (Refresh)
    else:
        order_id = request.session.get('last_order_id')
        if order_id:
            try:
                order = Orders.objects.get(id=order_id)
                return render(request, 'customer/confirmed.html', {'order': order})
            except Orders.DoesNotExist:
                pass
        return render(request, 'customer/order_failed.html', {'message': "No recent order found."})

























































@login_required(login_url='/customer_portal/login/')
def home(request):
    return render(request, 'customer/home_page.html')





def contact(request):
    return render(request, 'customer/contact.html')


def about(request):
    return render(request, 'customer/about.html')


def index(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/customer_portal/home/')
    return HttpResponseRedirect('/customer_portal/login/')


def login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/customer_portal/home/')
    return render(request, 'customer/login.html')


def auth_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/customer_portal/home/')
    
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        try:
            customer = Customer.objects.get(user=user)
        except Customer.DoesNotExist:
            customer = None

        if customer is not None and user is not None:
            auth_login(request, user)  # use alias to avoid conflict with function name 'login'
            return HttpResponseRedirect('/customer_portal/home/')
        else:
            return render(request, 'customer/login_failed.html')
    
    # default: just reload login page if GET request
    return HttpResponseRedirect('/customer_portal/login/')


def logout_view(request):
    auth.logout(request)
    return render(request, 'customer/login.html')


def register(request):
    return render(request, 'customer/register.html')


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
    birthday_str = request.POST.get('birthday')  # ✅ Birthday field

    # 🔹 Age calculation
    try:
        birth_date = date.fromisoformat(birthday_str)  # expects YYYY-MM-DD
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    except:
        messages.error(request, "Invalid birthday format.")
        return render(request, 'customer/register.html')

    # 🔹 Age restriction
    if age < 18:
        messages.error(request, "You must be at least 18 years old to register.")
        return render(request, 'customer/register.html')

    # Original registration logic
    try:
        user = User.objects.create_user(username=username, password=password, email=email)
        user.first_name = firstname
        user.last_name = lastname
        user.save()
    except:
        return render(request, 'customer/registration_error.html')

    try:
        area = Area.objects.get(city=city, pincode=pincode)
    except:
        area = None

    if area is not None:
        customer = Customer(user=user, mobile=mobile, area=area)
    else:
        area = Area(city=city, pincode=pincode)
        area.save()
        area = Area.objects.get(city=city, pincode=pincode)
        customer = Customer(user=user, mobile=mobile, area=area)

    customer.save()
    return render(request, 'customer/registered.html')


@login_required
def search(request):
    return render(request, 'customer/search.html')


@login_required
def search_results(request):
    city = request.POST['city']
    city = city.lower()
    vehicles_list = []
    
    # Kuhanin ang lahat ng Area na tumutugma sa city
    area = Area.objects.filter(city=city)
    
    for a in area:
        vehicles = Vehicles.objects.filter(area=a)
        for car in vehicles:
            if car.is_available == True:
                vehicle_dictionary = {
                    'name': car.car_name,
                    'color': car.color,
                    'id': car.id,
                    'pincode': car.area.pincode,
                    'city': car.area.city,     # <--- DAGDAGAN MO NITO PARA LUMABAS ANG LOCATION
                    'capacity': car.capacity,
                    'description': car.description
                }
                vehicles_list.append(vehicle_dictionary)
                
    request.session['vehicles_list'] = vehicles_list
    return render(request, 'customer/search_results.html')


@login_required
def rent_vehicle(request):
    id = request.POST['id']
    vehicle = Vehicles.objects.get(id=id)
    cost_per_day = vehicle.price_per_day
    return render(request, 'customer/confirmation.html', {'vehicle': vehicle, 'cost_per_day': cost_per_day})














































@login_required
def manage(request):
    user = request.user 
    orders = Orders.objects.filter(user=user)
    
    today = date.today()
    order_list = []

    for o in orders:
        delta = o.return_date - today
        remaining_days = delta.days
        
        penalty = 0
        if remaining_days < 0 and not o.is_complete:
            penalty = abs(remaining_days) * 500
        
        # 🔹 BAGUHIN ANG STATUS LOGIC:
        if o.is_complete:
            current_status = "Returned"
        elif o.is_pending:
            current_status = "Pending Approval" # Ito ang lalabas sa UI
        else:
            current_status = "Active"
            
        order_dictionary = {
            'id': o.id,
            'rent': o.rent,
            'vehicle': o.vehicle,
            'rental_date': o.rental_date,
            'return_date': o.return_date,
            'dest': o.description,
            'remaining_days': remaining_days,
            'penalty': penalty,
            'status': current_status,
            'is_complete': o.is_complete,
            'is_pending': o.is_pending, # Idagdag ito para mabasa ng HTML template
        }
        order_list.append(order_dictionary)
        
    return render(request, 'customer/manage.html', {'od': order_list})

@login_required
def return_vehicle(request):
    if request.method == "POST":
        order_id = request.POST.get('id')
        feedback = request.POST.get('feedback')
        order = Orders.objects.get(id=order_id)
        
        # 1. Kuhanin muna ang lumang destination/description
        old_description = order.description if order.description else "No destination"
        
        # 2. 🔹 BAGUHIN ITO: Pagsamahin ang Destination at Feedback
        # Gagamit tayo ng f-string para malinis ang format
        order.description = f"DESTINATION: {old_description} | FEEDBACK: {feedback}"
        
        # 3. I-set sa pending para kay admin
        order.is_pending = True 
        order.save()
        
        messages.success(request, "Return request sent. Waiting for Admin approval.")
        return HttpResponseRedirect('/customer_portal/manage/')

@login_required
def cancel_rental(request):
    if request.method == "POST":
        order_id = request.POST.get('id')
        order = Orders.objects.get(id=order_id)
        
        # Gawing available ulit ang kotse
        vehicle = order.vehicle
        vehicle.is_available = True
        vehicle.save()
        
        # Imbis na burahin, markahan lang natin
        order.is_complete = True
        # Nilalagyan natin ng marker ang description para mabasa ng HTML mamaya
        order.description = "CANCELLED_ORDER" 
        order.save()
        
        messages.success(request, "Successfully Cancelled")
        return HttpResponseRedirect('/customer_portal/manage/')

@login_required
def update_order(request):
    order_id = request.POST['id']
    order = Orders.objects.get(id=order_id)
    vehicle = order.vehicle
    vehicle.is_available = True
    vehicle.save()
    car_dealer = order.car_dealer
    car_dealer.wallet -= int(order.rent)
    car_dealer.save()
    order.delete()
    cost_per_day = vehicle.price_per_day
    return render(request, 'customer/confirmation.html', {'vehicle': vehicle}, {'cost_per_day': cost_per_day})


@login_required
def delete_order(request):
    order_id = request.POST['id']
    order = Orders.objects.get(id=order_id)
    car_dealer = order.car_dealer
    car_dealer.wallet -= float(order.rent)
    car_dealer.save()
    vehicle = order.vehicle
    vehicle.is_available = True
    vehicle.save()
    order.delete()
    return HttpResponseRedirect('/customer_portal/manage/')


def forgot_password(request):
    """
    Landing page for users who clicked 'Forgot Password'.
    Just renders the forgot password template.
    """
    return render(request, 'customer/forgot_password.html')












def reset_password_view(request):
    """
    Handles password reset form submission.
    Checks if username exists and if passwords match,
    then updates the user's password.
    """
    if request.method == "POST":
        username = request.POST.get("username")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        # ✅ Check kung may ganitong user
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, "Username not found.")
            return render(request, 'customer/forgot_password.html')

        # ✅ Check kung pareho ang password fields
        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'customer/forgot_password.html')

        # ✅ Update the password securely
        user.set_password(new_password)
        user.save()

        # ✅ Redirect sa success page
        return HttpResponseRedirect('/customer_portal/password_reset_success/')

    # Default: reload the forgot password page
    return render(request, 'customer/forgot_password.html')


def password_reset_success(request):
    """
    Displays confirmation message after password reset.
    """
    return render(request, 'customer/password_reset_success.html')

























