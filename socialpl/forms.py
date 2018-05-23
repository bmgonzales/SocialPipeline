from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Post, Authorized_Accts
from .timeset import *
from datetime import timedelta, datetime


def roundTime():
    dt = datetime.now()
    dateDelta = timedelta(minutes=15)
    roundTo = dateDelta.total_seconds()
    seconds = (dt - dt.min).seconds
    rounding = (seconds+roundTo) // roundTo * roundTo
    default_time = dt + timedelta(0,rounding-seconds,-dt.microsecond)
    default_time = default_time.strftime('%H:%M:%S')
    return default_time

default_time = roundTime()

class NewPost(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		user = kwargs.pop('user', None)
		super(NewPost, self).__init__(*args, **kwargs)
		self.initial['sched_time'] = default_time
		if user:
			self.fields['account'] = forms.ModelChoiceField(queryset=Authorized_Accts.objects.filter(user=user))

	text = forms.CharField(widget=forms.Textarea(), max_length=4000, label="Status")
	media = forms.ImageField(required=False, label='Upload Image')
	sched_date = forms.DateField(input_formats=['%Y-%m-%d'], label='Schedule Date')
	sched_time = forms.ChoiceField(choices=TIMESET, label='Schedule Time')

	class Meta:
		model = Post
		widgets = {'sched_date': forms.TextInput(attrs={'class':'datepicker'}),}
		fields = ['account', 'text', 'media', 'sched_date', 'sched_time']

class SignUpForm(UserCreationForm):
    email = forms.CharField(max_length=254, required=True, widget=forms.EmailInput())
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
