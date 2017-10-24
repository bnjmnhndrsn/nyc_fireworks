import os
import tweepy

C_KEY = os.environ.get('TWITTER_CONSUMER_KEY')
C_SECRET = os.environ.get('TWITTER_CONSUMER_SECRET')
A_TOKEN = os.environ.get('TWITTER_ACCESS_TOKEN')
A_TOKEN_SECRET = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')

def tweet(message):    
    auth = tweepy.OAuthHandler(C_KEY, C_SECRET)  
    auth.set_access_token(A_TOKEN, A_TOKEN_SECRET)  
    api = tweepy.API(auth)
    return api.update_status(message)
