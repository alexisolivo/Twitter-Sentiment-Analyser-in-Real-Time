import json
# Twitter API Access Keys
import datetime
import time

import tweepy
from tweepy import OAuthHandler
from tweepy import Stream
from kafka import KafkaProducer

import tweepy
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

WORDS_TO_TRACK = ["COVID","coronavirus"]

CONSUMER_KEY = os.environ.get("CONSUMER_KEY")
CONSUMER_SECRET = os.environ.get("CONSUMER_SECRET")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.environ.get("ACCESS_TOKEN_SECRET")

def verify_access():
    # Authenticate to Twitter
    auth = tweepy.OAuthHandler(CONSUMER_KEY, 
        CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, 
        ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)
    print('\nAuthenticating Twitter Credentials. Please wait......')
    time.sleep(3)
    try:
        status = api.verify_credentials()
        if status:
            print("\nTwitter Authentication Successful.\n")
            return True
        else:
            print('\nInvalid Twitter Credentials.\n')
            print('Exiting....\n')
            return False
    except:
        print("\nError during Twitter Authentication.\n")
        return False

def check_broker_status():
    kafka_producer = ''
    kafka_producer_server = KafkaConfig().get_producer_server()
    time.sleep(2)
    print('Checking Kafka Broker status....\n')
    time.sleep(3)
    try:
        kafka_producer = KafkaProducer(bootstrap_servers=kafka_producer_server)
        print('Kafka brokers are running at 9092.')
        return True
    except:
        print('No Kafka brokers are running at 9092. Please start Kafka server.')
        print('\nExiting....\n')
        return False


class KafkaConfig():
    def __init__(self):
        self.producer_server = 'localhost:9092' #Same port as your Kafka server

    def get_producer_server(self):
        return self.producer_server

class TwitterConfig():
    def __init__(self):
        self._consumer_key = tc.consumer_key
        self._consumer_secret = tc.consumer_secret
        self._access_token = tc.access_token
        self._access_token_secret = tc.access_token_secret
    
    def get_consumer_key(self):
        return self._consumer_key
    
    def get_consumer_secret(self):
        return self._consumer_secret

    def get_access_token(self):
        return self._access_token

    def get_access_token_secret(self):
        return self._access_token_secret



class TwitterAuth():
    """SET UP TWITTER AUTHENTICATION"""

    def authenticate_twitter_app(self):

        twitter_config = TwitterConfig()
        auth = OAuthHandler(twitter_config.get_consumer_key(), twitter_config.get_consumer_secret())
        auth.set_access_token(twitter_config.get_access_token(), twitter_config.get_access_token_secret())
        return auth
        

class TwitterStreamer():

    """SET UP STREAMER"""
    def __init__(self):
        self.TwitterAuth = TwitterAuth()

    def stream_tweets(self):
        i = 0
        while True:
            try:
                listener = ListenerTS() 
                auth = self.TwitterAuth.authenticate_twitter_app()
                stream = Stream(auth, listener)
                stream.filter(track = WORDS_TO_TRACK, stall_warnings=True, languages= ["en"])
            except:
                print('Connection reset by peer!!')
                pass
            


class ListenerTS(tweepy.StreamListener):
   
    def on_data(self, data):

            kafka_producer = ''
            kafka_producer_server = KafkaConfig().get_producer_server()

            kafka_producer = KafkaProducer(bootstrap_servers=kafka_producer_server)
                
            if kafka_producer != '':
                topic_name = "twitterdata"
                tweet = json.loads(data)
                tweet_text = ""
                #Check if the tweet has the keys lang and created_at and whether its in english
                if all(x in tweet.keys() for x in ['lang', 'created_at']) and tweet['lang'] == 'en':
                    if 'retweeted_status' in tweet.keys():
                        if 'quoted_status' in tweet['retweeted_status'].keys():
                            if('extended_tweet' in tweet['retweeted_status']['quoted_status'].keys()):
                                tweet_text = tweet['retweeted_status']['quoted_status']['extended_tweet']['full_text']
                            elif 'extended_tweet' in tweet['retweeted_status'].keys():
                                tweet_text = tweet['retweeted_status']['extended_tweet']['full_text']
                    elif tweet['truncated'] == 'true':
                        tweet_text = tweet['extended_tweet']['full_text']

                    else:
                        tweet_text = tweet['text']

                if tweet_text:
                    data = {
                        'created_at': tweet['created_at'],
                        'tweet': tweet_text
                    }

                    kafka_producer.send(topic_name, value = json.dumps(data).encode('utf-8'))
                    print('----------------------------------------------------------------------------------------------------------')
                    print(f"[{tweet['created_at']}]:{tweet_text}")
                    print('----------------------------------------------------------------------------------------------------------')
                    time.sleep(3)

    def on_error(self, status):
        # 420 error happens due to rate limiting
        if(status == 420): 
            #returning False in on_data disconnects the stream
            return False 
      

if __name__ == "__main__":
    
    if verify_access() and check_broker_status():
        TS = TwitterStreamer()
        TS.stream_tweets()