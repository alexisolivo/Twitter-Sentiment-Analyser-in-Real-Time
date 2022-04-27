'''
This script is used to train the ML Pipeline using the sentiment140 dataset
'''
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json,col,udf,explode,split
from pyspark.sql.types import StructType,StringType,StructField,ArrayType
from pyspark import SparkContext
from pyspark.sql import SQLContext
import re
from pyspark.ml.feature import StopWordsRemover,Tokenizer,\
HashingTF,IDF,Normalizer,CountVectorizer,StringIndexer

from pyspark.ml import Pipeline

from pyspark.ml.clustering import KMeans
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.ml.classification import LogisticRegression

from pathlib import Path
SRC_DIR = Path(__file__).resolve().parent


sc = SparkContext() 
sqlc = SQLContext(sc)

import os
os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-streaming-kafka-0-10_2.12:3.2.0,org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0 pyspark-shell'

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
    
    #Split the sentence into words
    temp = temp.split()
    return temp

'''
Sentiment140 allows you to discover the sentiment of a brand, product, 
or topic on Twitter.

The data is a CSV with emoticons removed. Data file format has 6 fields:

c0 - the polarity of the tweet (0 = negative,a4 = positive)
c1 - the id of the tweet (2087)
c2 - the date of the tweet (Sat May 16 23:58:44 UTC 2009)
c3 - the query (lyx). If there is no query, then this value is NO_QUERY.
c4 - the user that tweeted (robotickilldozr)
c5 - the text of the tweet (Lyx is cool)
'''
dataset_path = './Training_Data/training_dataset.csv'


df = (
    sqlc
    .read.format("com.databricks.spark.csv")
    .options(header=False) 
    .load(dataset_path)
    .selectExpr("_c0 as sentiment", "_c5 as tweet") 
)

df.printSchema()

pre_process = udf(lambda x: clean_tweet(x),ArrayType(StringType()))

df = df.withColumn("processed_data", pre_process(df.tweet)).dropna()

# Split the dataframe intl training and testing data

train, test = df.randomSplit([0.8,0.2], seed = 13)

#### Create an ML Pipeline
'''
Create an ML Pipeline. This performa TF-IDP calculation and Logistic Regression.
Logistive regression is a predictive analysis.

TF-IDF (term frequency-inverse document frequency) is a statistical measure that 
evaluates how relevant a word is to a document in a collection of documents.

This is done by multiplying two metrics:how many times a word appears in a document(TF), 
and the inverse document frequency(IDF) of the word across a set of documents.
'''

stop_word_remover = StopWordsRemover(inputCol="processed_data", outputCol="words")
vectorizer = CountVectorizer(inputCol="words", outputCol="tf")
idf = IDF(inputCol="tf", outputCol="features", minDocFreq=3)
label_indexer = StringIndexer(inputCol = "sentiment", outputCol = "label")
logistic_regression = LogisticRegression(maxIter=100)

pipeline = Pipeline(stages=[stop_word_remover, vectorizer, idf, label_indexer, logistic_regression])

#### Fit the pipeline to training dataframe.
'''
A pipeline is an Estimator.Calling the Pipeline fit() method with training data 
passes it through the Estimator stages to produce a Transformer or PipelineModel.
'''
training_model = pipeline.fit(train)

#### Make predictions based on the test data
'''
The pipeline model is used at test time.
Now when you run the transfrom method of the Transformer with test data
it passes data through transformer stages to give final predicitons.
'''
predictions = training_model.transform(test)

predictions.show(100)
predictions.withColumn('words', col('words').cast('string'))
predictions.withColumn('processed_data', col('processed_data').cast('string'))
predictions.printSchema()

evaluator = BinaryClassificationEvaluator(rawPredictionCol="rawPrediction")
accuracy = evaluator.evaluate(predictions)
print('\n***********************************************')
print(f"Accuray of prediction: {accuracy}") 
print('\n***********************************************')

model_path = str(SRC_DIR.joinpath('models'))

training_model.write().overwrite() \
    .save(model_path)

