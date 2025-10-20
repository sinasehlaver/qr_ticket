from django.contrib import admin
from .models import Event, Ticket
from django.utils.html import format_html

class TicketInline(admin.TabularInline):
    model = Ticket
    fields = ('attendee_name', 'plus_ones', 'status', 'created_at', 'view_qr')
    readonly_fields = ('view_qr', 'created_at')
    extra = 0
    can_delete = False

    def view_qr(self, obj):
        if obj.qr_code:
            return format_html('<a href="{}" target="_blank">QR</a>', obj.qr_code.url)
        return '-'
    view_qr.short_description = 'QR'

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'date_time', 'location', 'max_tickets', 'tickets_sold')
    inlines = [TicketInline]

    def tickets_sold(self, obj):
        return obj.tickets_sold
    tickets_sold.short_description = 'Satılan Biletler'

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('unique_id', 'attendee_name', 'event', 'plus_ones', 'status', 'created_at', 'qr_preview')
    list_filter = ('status', 'event')
    search_fields = ('attendee_name', 'unique_id')

    def qr_preview(self, obj):
        if obj.qr_code:
            return format_html('<img src="{}" style="height:60px;"/>', obj.qr_code.url)
        return '-'
    qr_preview.short_description = 'QR'
