
from django.contrib import admin
from django.urls import path
from superAdmin import views



urlpatterns = [

    path('Dashboard/', views.Dashboard, name='dashboard'),
    path('Table_Nat/', views.Table_Nat, name='table_nat'),
    path('Table_Filter/', views.Table_Filter, name='table_filter'),
    path('Gestion_Users/', views.Gestion_Users, name='gestion_users'),
    path('connexion/', views.connexion, name='connexion'),
    path('add_user/', views.request_admin, name='add_user'),
    path('ajout_filter/', views.ajout_filter, name='ajout_filter'),
    path('supprimer_filter/<int:pk>/', views.supprimer_filter, name='supprimer_filter'), 
    path('modifier_filter/', views.modifier_filter, name="modifier_filter"),
    path('ajouter_nat/', views.ajouter_nat, name='ajouter_nat'),
    path('supprimer_nat/<int:pk>/', views.supprimer_nat, name='supprimer_nat'), 
    path('modifier_nat/', views.modifier_nat, name="modifier_nat"),
    path('modifier_suggestion/', views.modifier_suggestion, name="modifier_suggestion"),
    path('supprimer_suggestion/', views.supprimer_suggestion, name="supprimer_suggestion"),
    path("appliquer_suggestion/<int:suggestion_id>/", views.appliquer_suggestion, name="appliquer_suggestion"),

]