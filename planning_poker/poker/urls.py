from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('createsession/', views.create_session),
    path('<str:id>/', views.session, name='session'),
]