from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView


app_name = 'tickets'

urlpatterns = [
    path('', views.home, name='home'),
    path('logout/', LogoutView.as_view(next_page='tickets:home'), name='logout'),
    path('events/', views.event_list, name='event_list'),
    path('events/add/', views.event_create, name='event_create'), 
    path('events/<int:event_id>/detail', views.event_detail, name='event_detail'),
    path('events/<int:event_id>/', views.event_landing, name='event_landing'),
    path('event/<int:event_id>/', views.event_landing, name='event_landing'),
    path('ticket/<uuid:ticket_uuid>/', views.ticket_display, name='ticket_display'),
    path('scanner/', views.scanner_dashboard, name='scanner_dashboard'),
    path('scanner/validate/', views.scanner_validate, name='scanner_validate'),
    path('api/check_ticket/<uuid:ticket_uuid>/', views.check_ticket, name='check_ticket'),
    path('api/use_ticket/<uuid:ticket_uuid>/', views.use_ticket, name='use_ticket'),
]
