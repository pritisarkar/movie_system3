from django.urls import path
from app import views
urlpatterns = [
    #user /login for admin
    path('user/',views.user,name="user"),
    path('login/',views.login,name="login"),
    path('GenreADD/',views.GenreADD,name="GenreADD"),
    path('GenreUPDATE/',views.GenreUPDATE,name="GenreUPDATE"),
    path('GenreDELETE/',views.GenreDELETE,name="GenreDELETE"),
    path("movieADD",views.movieADD,name="movieADD"),
    path("movieUpdae",views.movieUpdate,name="movieUpdate"),
    path("movieDelete",views.movieDelete,name="movieDelete"),
    path("signout",views.signout,name="signout"),
    path("customer",views.customer,name="customer"),
    path("loginCustomer",views.loginCustomer,name="loginCustomer"),
    path("signoutCustomer",views.signoutCustomer,name="signoutCustomer"),
     path("customerprofile",views.customerprofile,name="customerprofile"),
    path("AddToWatchedListView",views.AddToWatchedListView,name="AddToWatchedListView"),
    path("DeleteFromWatchedListView",views.DeleteFromWatchedListView,name="DeleteFromWatchedListView"),
    #watched-list
    path("DeleteFromWatchedListView",views.DeleteFromWatchedListView,name="DeleteFromWatchedListView"),
    #admin_dashboard
    path("admin_dashboard",views.admin_dashboard,name="admin_dashboard")
]
