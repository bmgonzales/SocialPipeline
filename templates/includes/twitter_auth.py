from birdy.twitter import UserClient


CONSUMER_KEY = CONSUMER_KEY
CONSUMER_SECRET = CONSUMER_SECRET
CALLBACK_URL = 'https://127.0.0.1:8000/register'		
		
client = UserClient(CONSUMER_KEY, CONSUMER_SECRET)
token = client.get_authorize_token(CALLBACK_URL)

ACCESS_TOKEN = token.oauth_token
ACCESS_TOKEN_SECRET = token.oauth_token_secret
TWITTER_URL = token.auth_url

OAUTH_VERIFIER = request.GET['oauth_verifier']
