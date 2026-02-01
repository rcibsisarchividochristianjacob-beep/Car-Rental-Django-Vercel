from django.urls import path, include, re_path
from customer_portal.views import *
from customer_portal import views as customer_views



urlpatterns = [
    re_path(r'^index/$', index),
    re_path(r'^login/$', login),
    re_path(r'^auth/$', auth_view),
    re_path(r'^logout/$', logout_view),
    re_path(r'^register/$', register),
    re_path(r'^registration/$', registration),
    re_path(r'^search/$', search),
    re_path(r'^search_results/$', search_results),
    re_path(r'^rent/$', rent_vehicle),
    re_path(r'^confirmation/$', confirm), 
    re_path(r'^manage/', manage),
    re_path(r'^update/', update_order),
    re_path(r'^delete/', delete_order),
    
    # TAMA NA DAPAT ITO (Tinanggal ang "views."):
    re_path(r'^cancel_order/', cancel_rental),
    re_path(r'^return_order/', return_vehicle),
    
    re_path(r'^forgot_password/$', forgot_password),
    re_path(r'^reset_password/$', reset_password_view),
    re_path(r'^password_reset_success/$', password_reset_success),
    re_path(r'^home/$', home),
]

