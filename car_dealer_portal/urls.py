from django.urls import path,include, re_path
from car_dealer_portal.views import *
# from django.conf.urls import url
from django.conf.urls.static import static

from django.urls import path
from . import views

urlpatterns = [
    re_path(r'^index/$',index),
    re_path(r'^login/$',login),
    re_path(r'^auth/$',auth_view),
    re_path(r'^logout/$',logout_view),
    re_path(r'^register/$',register),
    re_path(r'^registration/$',registration),
    re_path(r'^add_vehicle/$',add_vehicle),
    re_path(r'^manage_vehicles/$',manage_vehicles),
    re_path(r'^order_list/$',order_list),
    re_path(r'^complete/$',complete),
    re_path(r'^history/$',history),
    re_path(r'^delete_vehicle/(?P<vehicle_id>\d+)/$', delete_vehicle),


    re_path(r'^home_page/$', home_page, name='home_page'),

re_path(r'^edit_vehicle/(?P<vehicle_id>\d+)/$', edit_vehicle),

 re_path('search_ajax/', views.search_ajax, name='search_ajax'),
re_path('admin-portal/chat/', views.admin_chat_hub, name='admin_chat_hub'),
]



