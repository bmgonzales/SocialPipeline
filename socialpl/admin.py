from django.contrib import admin
from .models import Authorized_Accts
from .models import Post

class AcctsAdmin(admin.ModelAdmin):
	list_display = ('id', 'user', 'profile_name', 'platform', 'fb_id', 'access_token', 'access_token_secret')
	list_filter = ('user',)

class PostAdmin(admin.ModelAdmin):
	list_display = ('id', 'text', 'media', 'sched_date', 'sched_time', 'posttime', 'account', 'user')
	list_filter = ('user', 'account')

admin.site.register(Authorized_Accts, AcctsAdmin)
admin.site.register(Post, PostAdmin)
