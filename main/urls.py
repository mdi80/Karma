from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    path("",views.index, name="index"),
    path("stand",views.stand,name="stand"),
    path("frame",views.frame,name="frame"),
    path("calcstand",views.calcStand,name="calcstand"),
    path("orders",views.orders,name="orders"),
    path("login",views.loginuser,name="login"),
    path("logout",views.logoutuser,name="logout"),
    path("calcFrame",views.calcFrame,name="calcFrame"),
    path("passchange",views.passchange,name="passchange"),
    path("addorder",views.addorder,name="addorder"),
    path("profile",views.profile,name="profile"),
    
]
