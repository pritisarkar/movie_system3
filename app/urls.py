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
    path("customer",views.customer,name="customer")
]
