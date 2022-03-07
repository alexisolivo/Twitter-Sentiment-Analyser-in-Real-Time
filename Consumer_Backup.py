from kafka import KafkaConsumer
import json
import time

topic_name = 'twitterdata'


consumer = KafkaConsumer(
    topic_name,
     bootstrap_servers=['localhost:9092'],
     auto_offset_reset='latest',
     enable_auto_commit=True,
     auto_commit_interval_ms =  5000,
     fetch_max_bytes = 128,
     max_poll_records = 100,

     value_deserializer=lambda x: json.loads(x.decode('utf-8')))



for message in consumer:
 tweets = json.loads(json.dumps(message.value))
 user_name = tweets["user"]["name"]
 tweet_text = tweets["text"]
 print('\n{0} tweeted:\n {1}\n'.format(user_name,tweet_text))
 time.sleep(2)