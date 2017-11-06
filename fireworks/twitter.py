import os
import tweepy

from nyc_fireworks import settings

C_KEY = os.environ.get('TWITTER_CONSUMER_KEY')
C_SECRET = os.environ.get('TWITTER_CONSUMER_SECRET')
A_TOKEN = os.environ.get('TWITTER_ACCESS_TOKEN')
A_TOKEN_SECRET = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')

def tweet(message):
    if settings.SEND_TO_TWITTER:
        auth = tweepy.OAuthHandler(C_KEY, C_SECRET)  
        auth.set_access_token(A_TOKEN, A_TOKEN_SECRET)  
        api = tweepy.API(auth)
        return api.update_status(message)
    else:
        print message
