from django.core.management import BaseCommand
from django.utils import timezone

from socialpl.models import Post, Authorized_Accts
from twitter import Twitter, OAuth
from datetime import datetime, timedelta
from pytz import timezone
import tzlocal
import requests

class Command(BaseCommand):

    def handle(self, *args, **options):

        CONSUMER_KEY = CONSUMER_KEY
        CONSUMER_SECRET = CONSUMER_SECRET

        start_time = datetime.now(timezone('UTC'))
        end_time = start_time + timedelta(minutes=15) #one day = 1440
        to_post = Post.objects.filter(posttime__gte=start_time, posttime__lt=end_time)

        for new_post in to_post:

            status = new_post.text
            account = new_post.account
            authorization = Authorized_Accts.objects.get(profile_name=account)
            platform = authorization.platform

            if platform == 'twitter':
                access_token = authorization.access_token
                access_token_secret = authorization.access_token_secret

                kwargs = {"status": status.encode("utf-8"),}
                if new_post.media:
                    img = Twitter(
                        domain='upload.twitter.com',
                        auth=OAuth(access_token, access_token_secret, CONSUMER_KEY, CONSUMER_SECRET)
                    )
                    uploads = []
                    contents = new_post.media.read()
                    uploads.append(img.media.upload(media=contents)["media_id_string"])
                    kwargs["media_ids"] = ",".join(uploads)

                tweet = Twitter(auth=OAuth(access_token, access_token_secret, CONSUMER_KEY, CONSUMER_SECRET))
                tweet.statuses.update(**kwargs)

            elif platform == 'facebook':
                FB_ID = authorization.fb_id
                ACCESS_TOKEN = authorization.access_token
                params = {"access_token": ACCESS_TOKEN}
                message = status.encode("utf-8")

                if new_post.media:
                    site = 'http://bmgonzales.pythonanywhere.com/media/'
                    params["url"] = "{0}{1}".format(site, new_post.media)
                    params["caption"] = message
                    requests.post("https://graph.facebook.com/v2.11/{0}/photos".format(FB_ID),data=params)

                else:
                    params["message"] = message
                    requests.post("https://graph.facebook.com/v2.11/{0}/feed".format(FB_ID),data=params)

