from django.contrib import admin
from .models import *


# Register your models here.
admin.site.register(Utilisateur)
admin.site.register(Regles_Filter)
admin.site.register(Regles_NAT)
admin.site.register(Regles_Mangle)
admin.site.register(Suggestions)