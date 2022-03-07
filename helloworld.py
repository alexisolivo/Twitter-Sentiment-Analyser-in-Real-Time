# # import tweepy
# # import json

# # CONSUMER_KEY = ''
# # CONSUMER_SECRET = ''
# # ACCESS_TOKEN = ''
# # ACCESS_TOKEN_SECRET = ''

# # auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
# # auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
# # api = tweepy.API(auth)

# # user_name= 'madhavmanohar'
# # followers = api.followers(user_name)

# # for follower in followers:
# #     print(follower.screen_name)


# from pyspark.sql import SparkSession
# from pyspark.sql.functions import from_json,col



# data = [('James','','Smith','1991-04-01','M',3000),
#   ('Michael','Rose','','2000-05-19','M',4000),
#   ('Robert','','Williams','1978-09-05','M',4000),
#   ('Maria','Anne','Jones','1967-12-01','F',4000),
#   ('Jen','Mary','Brown','1980-02-17','F',-1)
# ]

# columns = ["firstname","middlename","lastname","dob","gender","salary"]

# spark = SparkSession.builder.appName('SparkByExamples.com').getOrCreate()

# df = spark.createDataFrame(data=data, schema = columns)

# """By using PySpark withColumn() on a DataFrame, we can cast or change the data 
# type of a column. In order to change data type, you would also need to use cast() 
# function along with withColumn(). The below statement changes the datatype from 
# String to Integer for the salary column."""

# #This is used to cast the column type to integer
# df.withColumn("salary",col("salary").cast("Integer")).show()

# #This is used to manipulate the value of column salary 
# df.withColumn("salary",col("salary")*1000).show()

# #This shows the schema of the dataframe
# df.printSchema()
from pathlib import Path
SRC_DIR = Path(__file__).resolve().parent
model_path = SRC_DIR.joinpath('models')
print(type(str(model_path)))