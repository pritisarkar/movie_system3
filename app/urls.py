from django.urls import path
from app import views
urlpatterns = [
    path('user/',views.user,name="user"),
    path('login/',views.login,name="login"),
    path('GenreADD/',views.GenreADD,name="GenreADD"),
    path('GenreUPDATE/',views.GenreUPDATE,name="GenreUPDATE"),
    path('GenreDELETE/',views.GenreDELETE,name="GenreDELETE"),
    path("movieADD",views.movieADD,name="movieADD")
]