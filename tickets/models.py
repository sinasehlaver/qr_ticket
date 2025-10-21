import uuid
import io
import os
from django.db import models
from django.utils import timezone
from django.core.files.base import ContentFile
import qrcode
from django.urls import reverse

def qr_upload_path(instance, filename):
    # store under media/qr_codes/<uuid>.png
    return f'qr_codes/{instance.unique_id}.png'

class Event(models.Model):
    name = models.CharField(max_length=255)
    date_time = models.DateTimeField()
    location = models.CharField(max_length=255)
    max_tickets = models.PositiveIntegerField(default=100)

    def __str__(self):
        return f"{self.name} @ {self.date_time.strftime('%Y-%m-%d %H:%M')}"

    def tickets_sold(self):
        return self.tickets.count()
    tickets_sold.short_description = "Tickets Sold"

class Ticket(models.Model):
    STATUS_UNUSED = 'unused'
    STATUS_USED = 'used'
    STATUS_CHOICES = [
        (STATUS_UNUSED, 'Girmedi'),
        (STATUS_USED, 'Girdi'),
    ]

    event = models.ForeignKey(Event, related_name='tickets', on_delete=models.CASCADE)
    attendee_name = models.CharField(max_length=255)
    plus_ones = models.PositiveIntegerField(default=0)
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    qr_code = models.ImageField(upload_to=qr_upload_path, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_UNUSED)
    created_at = models.DateTimeField(auto_now_add=True)
    checked_in_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Ticket {self.unique_id} for {self.attendee_name}"
    
    def get_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, 'Unknown')

    def get_absolute_url(self):
        return reverse('tickets:ticket_display', kwargs={'ticket_uuid': str(self.unique_id)})

    def save(self, *args, **kwargs):
        # Save instance first if no qr yet to ensure unique_id exists
        creating = self.pk is None
        super().save(*args, **kwargs)

        # generate qr if not present
        if not self.qr_code:
            qr_data = str(self.unique_id)
            qr_img = qrcode.make(qr_data)
            buffer = io.BytesIO()
            qr_img.save(buffer, format='PNG')
            filename = f"{self.unique_id}.png"
            self.qr_code.save(filename, ContentFile(buffer.getvalue()), save=False)
            buffer.close()
            # Save again to persist qr_code
            super().save(update_fields=['qr_code'])
