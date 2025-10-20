from django import forms
from .models import Ticket

class TicketCreateForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['attendee_name', 'plus_ones']

    attendee_name = forms.CharField(label='Adınız ve Soyadınız', max_length=255, widget=forms.TextInput(attrs={'class': 'form-control', 'required': True}))
    plus_ones = forms.IntegerField(label='Kaç kişi daha getireceksiniz? (plus_ones)', min_value=0, initial=0, widget=forms.NumberInput(attrs={'class': 'form-control'}))
