import json
import time
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json,col,udf,explode,split
from pyspark.sql.types import StructType,StringType,StructField,ArrayType
import math
import string
import random
import re
from pyspark.ml import PipelineModel
from pathlib import Path
SRC_DIR = Path(__file__).resolve().parent
import os
os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-streaming-kafka-0-10_2.12:3.2.1,org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0,io.delta:delta-core_2.12:1.1.0,org.mongodb.spark:mongo-spark-connector_2.12:3.0.1 pyspark-shell'
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

KAFKA_TOPIC_NAME = os.environ.get("KAFKA_TOPIC_NAME")
KAFKA_BOOTSRAP_SEVER = os.environ.get("KAFKA_BOOTSRAP_SEVER")
MONGO_CONN = os.environ.get("MONGO_CONN")
working_directory = 'jars/*'
"""
Spark Session:

SparkSession is the entry point to Spark SQL. 
It is one of the very first objects you create while developing a Spark SQL 
application.
As a Spark developer, you create a SparkSession using the SparkSession.
builder method (that gives you access to Builder API that you use to configure the session).
"""


def clean_tweet(tweet):
    
    temp = tweet.lower()
    #Remove any hashtags and mentions in tweet:
    temp = re.sub("@[A-Za-z0-9_]+","", temp)
    temp = re.sub("#[A-Za-z0-9_]+","", temp)
    
    #Removing any links in the tweet:
    temp = re.sub(r"http\S+", "", temp)
    temp = re.sub(r"www.\S+", "", temp)
    
    #Removing any punctuations such as period, comma, exclamation mark, question mark, etc:
    temp = re.sub('[()!?]', ' ', temp)
    temp = re.sub('\[.*?\]',' ', temp)
    
    #Remove any stop words:
    '''
    What is a stop word? Stop words are words that are considered unimportant to the meaning of a text. These words may seem important to us, 
    humans, but to machine these words may be considered nuisance to the processing steps.

    It’s also important to keep in mind that stop words are largely language-dependent. In English, you have stop words such as for, to, 
    and, or, in, out, etc. 
    '''
    #Split the sentence into words
    temp = temp.split()

    stopwords = ["for", "on", "an", "a", "of", "and", "in", "the", "to", "from"]
    temp = [w for w in temp if not w in stopwords]
 
    return temp


if __name__ == '__main__':

    schema = StructType([StructField("text", StringType(), True)])


    spark = SparkSession.builder.master("local[*]").appName("SentimentApp") \
    .config("spark.mongodb.input.uri", MONGO_CONN) \
    .config("spark.mongodb.output.uri", MONGO_CONN) \
    .config('spark.jars.packages', 'org.mongodb.spark:mongo-spark-connector_2.12:3.0.1')\
    .getOrCreate()

    schema = StructType(
        [StructField('created_at', StringType()),
            StructField('tweet', StringType()),
            StructField('search_word', StringType())
            ]
    )

    kafka_df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BOOTSRAP_SEVER) \
    .option("subscribe", KAFKA_TOPIC_NAME) \
    .option("header","true") \
    .load() \
    .selectExpr("CAST(timestamp AS TIMESTAMP) as timestamp", "CAST(value AS STRING) as tweet")
    
    kafka_df = kafka_df \
    .withColumn("value", from_json("tweet", schema)) \
    .select('timestamp', 'value.*')


    pre_process = udf(lambda x : clean_tweet(x), ArrayType(StringType()))

    kafka_df = kafka_df.withColumn("processed_data", pre_process(kafka_df.tweet)).dropna()

    #### Passing the dataframe to ml pipeline

    model_path = str(SRC_DIR.joinpath('models'))
    
    pipeline_model = PipelineModel.load(model_path)

    prediction_df = pipeline_model.transform(kafka_df)

    '''
    Prediction Value:
    Positive  as 0.0 
    Negative  as 1.0
    '''

    sentiment_udf = udf(lambda x : 'Positive' if x == 0.0 else 'Negative', StringType())

    prediction_df = prediction_df\
        .select('search_word','processed_data','created_at','timestamp','tweet','prediction')
    #Creates new column with the sentiment output
    prediction_df = prediction_df.withColumn('sentiment', sentiment_udf(prediction_df.prediction))

    #Write to mongoDB in batches
    def write_row(batch_df , batch_id):
        batch_df.write.format("com.mongodb.spark.sql.DefaultSource").mode("append").save()
        pass

    prediction_df.writeStream.foreachBatch(write_row).start().awaitTermination()
