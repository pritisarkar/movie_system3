from django.urls import path
from app import views
urlpatterns = [
    #user /login for admin
    path('user/',views.user,name="user"),
    path('login/',views.login,name="login"),
    path('GenreADD/',views.GenreADD,name="GenreADD"),
    path('GenreUpdate/<int:genre_id>/',views.GenreUPDATE,name="GenreUPDATE"),
    path('GenreDELETE/<int:genre_id>/',views.GenreDELETE,name="GenreDELETE"),
    path('movieADD/', views.movieADD, name='movieADD'),
    path("movieUpdate/<int:movie_id>/",views.movieUpdate,name="movieUpdate"),
    path("movieDelete/<int:movie_id>/",views.movieDelete,name="movieDelete"),
    path('signout/', views.signout, name='signout'),
    path("customer/",views.customer,name="customer"),
    path("loginCustomer/",views.loginCustomer,name="loginCustomer"),
    path("signoutCustomer/",views.signoutCustomer,name="signoutCustomer"),
    path("customerprofile/<int:customer_id>/",views.customerprofile,name="customerprofile"),
    path("AddToWatchedListView/",views.AddToWatchedListView,name="AddToWatchedListView"),
    path("DeleteFromWatchedListView/",views.DeleteFromWatchedListView,name="DeleteFromWatchedListView"),
    path("admin_dashboard/",views.admin_dashboard,name="admin_dashboard"),
    path("client_dashboard/",views.client_dashboard,name="client_dashboard"),
    path('user/dashboard/', views.user_dashboard, name='user_dashboard'),
    path('dashboard/', views.customer_dashboard, name='customer_dashboard'),
]
