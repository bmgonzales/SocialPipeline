from django.db import models
from django.contrib.auth.models import User
from .timeset import *
from datetime import date, timedelta, datetime, time
from django.utils.crypto import get_random_string


class Authorized_Accts(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	platform = models.CharField(max_length=10, choices=(('twitter', 'Twitter'), ('facebook', 'Facebook')))
	profile_name = models.CharField(max_length=100)
	fb_id = models.CharField(max_length=200, blank=True, null=True)
	access_token = models.CharField(max_length=300)
	access_token_secret = models.CharField(max_length=300, blank=True, null=True)

	def __str__(self):
		return self.profile_name

def user_dir(instance, filename):
	ext = filename.split('.')[-1]
	uid = uid = get_random_string(length=16, allowed_chars=u'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
	post_date = instance.sched_date
	userid = instance.user
	filename = '{0}/{1}/{2}.{3}'.format(userid, post_date, uid, ext)
	return filename

class Post(models.Model):
	text = models.TextField(max_length=4000)
	media = models.ImageField(upload_to=user_dir, blank=True, null=True)
	sched_date = models.DateField()
	sched_time = models.CharField(max_length=20, choices=TIMESET)
	account = models.ForeignKey(Authorized_Accts, related_name='accounts', on_delete=models.CASCADE)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	posttime = models.CharField(max_length=20)

	def __str__(self):
		return str(self.id)
