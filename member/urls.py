from django.urls import path
from . import views

app_name = 'member'

urlpatterns = [
    path('identitas/', views.identitas_view, name='identitas'),
    path('klaim/', views.klaim_view, name='klaim'),
    path('transfer/', views.transfer_view, name='transfer'),
    path('redeem/', views.redeem_view, name='redeem'),
    path('package/', views.package_view, name='package'),
    path('info-tier/', views.info_tier_view, name='info_tier'),
]