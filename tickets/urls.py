from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView


app_name = 'tickets'

urlpatterns = [
    path('', views.home, name='home'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('event/<int:event_id>/', views.event_landing, name='event_landing'),
    path('ticket/<uuid:ticket_uuid>/', views.ticket_display, name='ticket_display'),
    path('scanner/', views.scanner_dashboard, name='scanner_dashboard'),
    path('scanner/validate/', views.scanner_validate, name='scanner_validate'),
    path('api/check_ticket/<uuid:ticket_uuid>/', views.check_ticket, name='check_ticket'),
    path('api/use_ticket/<uuid:ticket_uuid>/', views.use_ticket, name='use_ticket'),
]
