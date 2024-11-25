
from django import forms


class AttendanceForm(forms.Form):
    entry_time = forms.TimeField(
        label='Giriş Saati',
        widget=forms.TimeInput(format='%H:%M', attrs={'type': 'time'})
    )