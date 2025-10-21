import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden, JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.csrf import csrf_exempt
from .models import Event, Ticket
from .forms import TicketCreateForm, EventForm
from django.contrib import messages
from django.utils import timezone


@require_GET
def auth_status(request):
    """Return whether the current session is authenticated (used by client-side redirect)."""
    return JsonResponse({'is_authenticated': request.user.is_authenticated})

def home(request):
    # Eğer kullanıcı zaten giriş yapmışsa, rolüne göre yönlendir

    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('tickets:event_list')
        else:
            if request.user.is_staff:
                return redirect('tickets:scanner_dashboard')

    # Login form işleme
    if request.method == 'POST':
        print("POST request received")

        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Hoş geldiniz {username}!')
                
                # Kullanıcı tipine göre yönlendirme
                if user.is_superuser:
                    return redirect('admin:index')
                else:
                    if request.user.is_staff:
                        return redirect('tickets:scanner_dashboard')
            else:
                messages.error(request, "Geçersiz kullanıcı adı veya şifre.")
        else:
            messages.error(request, "Geçersiz kullanıcı adı veya şifre.")
    else:
        print("GET request received")
        form = AuthenticationForm()
    
    return render(request, 'tickets/home.html', {'form': form})

def event_list(request):
    # Simple list of upcoming events
    print("Fetching event list")
    events = Event.objects.order_by('date_time')
    add_form = EventForm() if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser) else None
    return render(request, 'tickets/event_landing.html', {'events': events, 'single_event_mode': False, 'add_form': add_form})

@login_required
def event_create(request):
    # only staff or superuser allowed
    if not (request.user.is_staff or request.user.is_superuser):
        return HttpResponseForbidden("Yetkiniz yok")
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save()
            messages.success(request, "Etkinlik oluşturuldu.")
            return redirect('tickets:event_landing', event_id=event.pk)
    else:
        form = EventForm()
    return render(request, 'tickets/event_add.html', {'form': form})

@login_required
def event_detail(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    tickets = Ticket.objects.filter(event=event).order_by('-checked_in_at', '-attendee_name')
    return render(request, 'tickets/event_detail.html', {'event': event, 'tickets': tickets})


def event_landing(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    # check max tickets
    total_reserved = event.tickets_sold()
    if request.method == 'POST':
        form = TicketCreateForm(request.POST)
        if form.is_valid():
            # Reject if over max_tickets
            total_after = total_reserved + 1 + form.cleaned_data['plus_ones']
            # Here we treat each ticket as 1 sale regardless of plus_ones; adjust if you want plus_ones to count toward max_tickets.
            if event.max_tickets is not None and event.tickets_sold() >= event.max_tickets:
                messages.error(request, "Etkinlik için bilet kalmamış.")
            else:
                ticket = form.save(commit=False)
                ticket.event = event
                ticket.save()
                return redirect(ticket.get_absolute_url())
    else:
        form = TicketCreateForm()
    return render(request, 'tickets/event_landing.html', {'event': event, 'form': form, 'single_event_mode': True})

def ticket_display(request, ticket_uuid):
    ticket = get_object_or_404(Ticket, unique_id=ticket_uuid)
    return render(request, 'tickets/ticket_display.html', {'ticket': ticket})

@login_required
def scanner_dashboard(request):
    # Allow admin or users in Scanner group or staff
    user = request.user
    is_scanner = user.is_staff or user.groups.filter(name='Scanner').exists() or user.is_superuser
    if not is_scanner:
        return HttpResponseForbidden("You are not authorized to access the scanner.")
    return render(request, 'tickets/scanner_dashboard.html')

@login_required
def check_ticket(request, ticket_uuid):
    """QR okunduğunda bilet bilgilerini getir"""
    try:
        ticket = Ticket.objects.get(unique_id=ticket_uuid)
        ticket_data = {
            'unique_id': str(ticket.unique_id),
            'attendee_name': ticket.attendee_name,
            'plus_ones': ticket.plus_ones,
            'status': ticket.status,
            'checked_in_at': ticket.checked_in_at,
            'created_at': ticket.created_at,
            'event_name': ticket.event.name,
            'event_date': ticket.event.date_time.strftime('%d.%m.%Y %H:%M'),
            'event_location': ticket.event.location
        }
        return JsonResponse({'success': True, 'ticket': ticket_data})
    except Ticket.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Bilet bulunamadı'})

@login_required
def use_ticket(request, ticket_uuid):
    """Bilet kullanıldı olarak işaretle"""
    try:
        ticket = Ticket.objects.get(unique_id=ticket_uuid)
        
        if ticket.status == 'used':
            return JsonResponse({
                'success': False, 
                'error': 'Bu bilet zaten kullanılmış'
            })
        
        ticket.status = 'used'
        ticket.save()
        
        return JsonResponse({
            'success': True, 
            'message': 'Bilet başarıyla kullanıldı'
        })
    except Ticket.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Bilet bulunamadı'})

@login_required
@require_POST
def scanner_validate(request):
    user = request.user
    is_scanner = user.is_staff or user.groups.filter(name='Scanner').exists() or user.is_superuser
    if not is_scanner:
        return JsonResponse({'ok': False, 'error': 'Not authorized'}, status=403)

    try:
        data = json.loads(request.body.decode('utf-8'))
        ticket_uuid = data.get('ticket_uuid')
    except Exception:
        return JsonResponse({'ok': False, 'error': 'Invalid JSON'}, status=400)

    if not ticket_uuid:
        return JsonResponse({'ok': False, 'error': 'No ticket_uuid provided'}, status=400)

    try:
        ticket = Ticket.objects.get(unique_id=ticket_uuid)
    except Ticket.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Ticket not found'}, status=404)

    if ticket.status == Ticket.STATUS_USED:
        return JsonResponse({'ok': False, 'error': 'Ticket already used'}, status=400)

    # Mark used
    ticket.status = Ticket.STATUS_USED
    ticket.save(update_fields=['status'])
    return JsonResponse({
        'ok': True,
        'message': 'Ticket checked-in successfully',
        'ticket': {
            'unique_id': str(ticket.unique_id),
            'attendee_name': ticket.attendee_name,
            'plus_ones': ticket.plus_ones,
            'event': ticket.event.name,
            'event_date': ticket.event.date_time.isoformat(),
            'event_location': ticket.event.location,
            'status': ticket.status,
        }
    })
