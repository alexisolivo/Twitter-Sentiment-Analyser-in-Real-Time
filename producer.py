import json
# Twitter API Access Keys

import tweepy
from tweepy import OAuthHandler
from tweepy import Stream
from kafka import KafkaProducer
import twitter_creds as tc

WORDS_TO_TRACK = ["Covid-19","coronavirus","covid"]


class KafkaConfig():
    def __init__(self):
        self.producer = KafkaProducer(bootstrap_servers='localhost:9092') #Same port as your Kafka server

    def get_producer(self):
        return self.producer

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
            i+=1
            print('{0}.Hello'.format(i))
            listener = ListenerTS() 
            auth = self.TwitterAuth.authenticate_twitter_app()
            stream = Stream(auth, listener)
            stream.filter(track = WORDS_TO_TRACK, stall_warnings=True, languages= ["en"])
            print(stream)


class ListenerTS(tweepy.StreamListener):
   
    def on_data(self, data):
            flag = True
            kafka_producer = KafkaConfig().get_producer()
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
    
    def on_error(self, status):
        # 420 error happens due to rate limiting
        if(status == 420): 
            #returning False in on_data disconnects the stream
            return False 
      

if __name__ == "__main__":
    TS = TwitterStreamer()
    TS.stream_tweets()