from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.conf import settings
from django.utils import timezone
from django.views.generic import UpdateView
from django.core.exceptions import ObjectDoesNotExist
from birdy.twitter import UserClient
import urllib, urllib.parse, requests
from datetime import datetime
from pytz import timezone
import tzlocal

from .forms import NewPost, SignUpForm
from .models import Post, Authorized_Accts


def index(request):
	return render(request, 'index.html')

def signup(request):
	if request.method == 'POST':
		form = SignUpForm(request.POST)
		if form.is_valid():
			user = form.save()
			login(request, user)
			return redirect('profile')
	else:
		form = SignUpForm()
	return render(request, 'signup.html', {'form': form})

#Twitter API credentials
CONSUMER_KEY = CONSUMER_KEY
CONSUMER_SECRET = CONSUMER_SECRET
CALLBACK_URL = 'http://bmgonzales.pythonanywhere.com/registered_twitter'

#Facebook API credentials
FB_APP_ID = FB_APP_ID
FB_APP_SECRET = FB_APP_SECRET
redirect_uri = 'http://bmgonzales.pythonanywhere.com/registered_facebook'

@login_required
def register(request, platform):

	if platform == 'twitter':
	#Twitter Authorization p1
		client = UserClient(CONSUMER_KEY, CONSUMER_SECRET)
		token = client.get_authorize_token(CALLBACK_URL)
		ACCESS_TOKEN = token.oauth_token
		request.session['ACCESS_TOKEN'] = ACCESS_TOKEN
		ACCESS_TOKEN_SECRET = token.oauth_token_secret
		request.session['ACCESS_TOKEN_SECRET'] = ACCESS_TOKEN_SECRET
		twitter_url = token.auth_url
		return render(request, 'register.html', {'twitter_url': twitter_url, 'platform': platform})

	elif platform == 'facebook':
	#Facebook Authorization p1
		attrs = {'client_id': FB_APP_ID, 'redirect_uri': redirect_uri, 'scope': 'public_profile, publish_actions, manage_pages'}
		facebook_url = 'https://graph.facebook.com/oauth/authorize?%s' % urllib.parse.urlencode(attrs)
		return render(request, 'register.html', {'facebook_url': facebook_url, 'platform': platform})


def registered_twitter(request):
	user = request.user
	platform = 'twitter'
	#Twitter Authorization p2
	ACCESS_TOKEN = request.session.get('ACCESS_TOKEN')
	ACCESS_TOKEN_SECRET = request.session.get('ACCESS_TOKEN_SECRET')
	client = UserClient(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
	OAUTH_VERIFIER = request.GET['oauth_verifier']
	token = client.get_access_token(OAUTH_VERIFIER)
	access_token = token.oauth_token
	access_token_secret = token.oauth_token_secret
	profile_name = token.screen_name
	Authorized_Accts.objects.create(
		user = user,
		platform = platform,
		profile_name = profile_name,
		access_token = access_token,
		access_token_secret = access_token_secret
	)
	return render(request, 'registered_twitter.html', {'platform': platform, 'profile_name': profile_name})

def registered_facebook(request):
	user = request.user
	platform = 'facebook'
	#Facebook Authorization p2
	code = request.GET.get('code')
	attrs = {'client_id': FB_APP_ID, 'client_secret': FB_APP_SECRET, 'code': code, 'redirect_uri': redirect_uri}
	token_url = 'https://graph.facebook.com/oauth/access_token?%s' % urllib.parse.urlencode(attrs)
	r = requests.get(token_url)
	r_json = r.json()
	access_token = r_json['access_token']
	graph_url = 'https://graph.facebook.com/v2.11/me?access_token=%s' % access_token
	g = requests.get(graph_url)
	g_json = g.json()
	profile_name = g_json['name']
	fb_id = g_json['id']
	Authorized_Accts.objects.create(
		user = user,
		platform = platform,
		profile_name = profile_name,
		fb_id = fb_id,
		access_token = access_token,
	)
	return render(request, 'registered_facebook.html', {'platform': platform, 'profile_name': profile_name})

@login_required
def dashboard(request):
	if request.method == 'POST':
		user = request.user
		utc_time = datetime.now(timezone('UTC'))
		posts = Post.objects.filter(user=user)
		upcoming = posts.filter(posttime__gte=utc_time).order_by('posttime')
		recent = posts.filter(posttime__lte=utc_time).order_by('-posttime')[:9]

		form = NewPost(request.POST, request.FILES, user=user)

		if form.is_valid():
			tz = str(tzlocal.get_localzone())
			dd = form.cleaned_data.get('sched_date') #datetime.date object
			t = form.cleaned_data.get('sched_time') #time string from form
			tt = datetime.strptime(t, '%H:%M:%S').time() #datetime.time object
			c = datetime.combine(dd, tt) #combined datetime naive object
			cloc = timezone(tz).localize(c) #assign to local timezone
			cutc = cloc.astimezone(timezone('UTC')) #convert to UTC timezone
			new_post = form.save(commit=False)

			new_post = Post.objects.create (
			text = form.cleaned_data.get('text'),
			media = form.cleaned_data.get('media'),
			sched_date = cloc.strftime('%Y-%m-%d'),
			sched_time = cloc.strftime('%-I:%M %p'),
			account = form.cleaned_data.get('account'),
			user = request.user,
			posttime = cutc
			)

			new_post.save()
			form = NewPost()

			return redirect('dashboard')

	else:
		user = request.user
		utc_time = datetime.now(timezone('UTC'))
		posts = Post.objects.filter(user=user)
		upcoming = posts.filter(posttime__gte=utc_time).order_by('posttime')
		recent = posts.filter(posttime__lte=utc_time).order_by('-posttime')[:9]

		form = NewPost(user=user)

		return render(request, 'dashboard.html', {'upcoming': upcoming, 'recent': recent, 'form': form})

@login_required
def delete_post(request, pk):
	del_post = Post.objects.get(pk = pk)
	del_post.delete()
	return redirect('dashboard')

@login_required
def edit_post(request, pk):
	edit_post = get_object_or_404(Post, pk=pk)
	if request.method == 'POST':
		user = edit_post.user
		utc_time = datetime.now(timezone('UTC'))
		posts = Post.objects.filter(user=user)
		upcoming = posts.filter(posttime__gte=utc_time).order_by('posttime')
		recent = posts.filter(posttime__lte=utc_time).order_by('-posttime')[:9]

		form = NewPost(request.POST, request.FILES, instance=edit_post)

		if form.is_valid():
			tz = str(tzlocal.get_localzone())
			edit_post = form.save(commit=False)
			edit_post.user = edit_post.user
			dd = edit_post.sched_date
			t = edit_post.sched_time
			tt = datetime.strptime(t, '%H:%M:%S').time()
			c = datetime.combine(dd, tt)
			cloc = timezone(tz).localize(c)
			edit_post.sched_date = cloc.strftime('%Y-%m-%d')
			edit_post.sched_time = cloc.strftime('%I:%M %p')
			edit_post.posttime = cloc.astimezone(timezone('UTC'))
			edit_post.save()
			form = NewPost()

		return redirect('dashboard')

	else:
		user = request.user
		utc_time = datetime.now(timezone('UTC'))
		posts = Post.objects.filter(user=user)
		upcoming = posts.filter(posttime__gte=utc_time).order_by('posttime')
		recent = posts.filter(posttime__lte=utc_time).order_by('-posttime')[:9]

		form = NewPost(instance=edit_post)
		edit = "edit"

		return render(request, 'dashboard.html', {'upcoming': upcoming, 'recent': recent, 'form': form, 'edit': edit})

@login_required
def profile(request):
	user = request.user
	t_ct = Authorized_Accts.objects.filter(user=user, platform='twitter').count()
	if t_ct > 0:
		t_acct = Authorized_Accts.objects.get(user=user, platform='twitter')
		t_name = t_acct.profile_name
		t_id = t_acct.id
		t_platform = 'twitter'
	else:
		t_name = ""
		t_id = ""
		t_platform = 'twitter'
	f_ct = Authorized_Accts.objects.filter(user=user, platform='facebook').count()
	platform = 'facebook'
	if f_ct > 0:
		f_acct = Authorized_Accts.objects.get(user=user, platform='facebook')
		f_name = f_acct.profile_name
		f_id = f_acct.id
		f_platform = 'facebook'
	else:
		f_name = ""
		f_id = ""
		f_platform = 'facebook'

	return render(request, 'profile.html', {'user': user, 't_id': t_id, 'f_id': f_id, 't_name': t_name, 'f_name': f_name, 't_platform': t_platform, 'f_platform': f_platform})

@login_required
def delete_acct(request, pk):
	del_acct = Authorized_Accts.objects.get(pk = pk)
	del_acct.delete()
	return redirect('profile')

@login_required
def delete_profile(request, username):
	del_user = User.objects.get(username=username)
	del_user.delete()
	return redirect('index')
