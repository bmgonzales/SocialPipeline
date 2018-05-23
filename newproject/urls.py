from django.contrib import admin
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from socialpl import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^signup/$', views.signup, name='signup'),
	url(r'^register/(?P<platform>[\w|\W.-]+)/$', views.register, name='register'),
	url(r'^registered_twitter$', views.registered_twitter, name='registered_twitter'),
	url(r'^registered_facebook$', views.registered_facebook, name='registered_facebook'),
	url(r'^login/$', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
	url(r'^logout/$', auth_views.LogoutView.as_view(), name='logout'),
	url(r'^dashboard/$', views.dashboard, name='dashboard'),
	url(r'^delete_post/(?P<pk>\d+)/$', views.delete_post, name='delete_post'),
	url(r'^edit_post/(?P<pk>\d+)/$', views.edit_post, name='edit_post'),
	url(r'^delete_acct/(?P<pk>\d+)/$', views.delete_acct, name='delete_acct'),
	url(r'^profile/$', views.profile, name='profile'),
	url(r'^delete_profile/(?P<username>[\w|\W.-]+)/$', views.delete_profile, name='delete_profile'),
	url(r'^admin/', admin.site.urls),

    url(r'^reset/$',
        auth_views.PasswordResetView.as_view(
            template_name='password_reset.html',
            email_template_name='password_reset_email.html',
            subject_template_name='password_reset_subject.txt'
        ),
        name='password_reset'),
    url(r'^reset/done/$',
        auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'),
        name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'),
        name='password_reset_confirm'),
    url(r'^reset/complete/$',
        auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),
        name='password_reset_complete'),

    url(r'^settings/password/$', auth_views.PasswordChangeView.as_view(template_name='password_change.html'),
        name='password_change'),
    url(r'^settings/password/done/$', auth_views.PasswordChangeDoneView.as_view(template_name='password_change_done.html'),
		name='password_change_done'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
