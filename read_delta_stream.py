'''
This script is used to read from the twitter data from the delta lake database
'''

from pyspark.sql import SparkSession
from pathlib import Path
from pyspark.sql.functions import col,concat_ws
import os
os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-streaming-kafka-0-10_2.12:3.2.0,org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0,io.delta:delta-core_2.12:1.1.0 pyspark-shell'


SRC_DIR = Path(__file__).resolve().parent



delta_output_path = str(SRC_DIR.parent.joinpath('delta/events/_checkpoints/twitter_sentiments'))

spark = SparkSession \
    .builder \
    .appName('APP') \
    .master("local[*]") \
    .enableHiveSupport() \
    .config("spark.sql.warehouse.dir", "target/spark-warehouse") \
    .config('spark.port.maxRetries', 100) \
    .getOrCreate()

delta_stream = spark.\
readStream.format("delta").\
load(delta_output_path)



# delta_stream \
#     .writeStream \
#     .format("console") \
#     .start() \
#     .awaitTermination()

sink_output_path = str(SRC_DIR.parent.joinpath('FileStore/tables/stream_csv/file_sink'))
checkpoint_output = str(SRC_DIR.parent.joinpath('FileStore/tables/stream_csv/checkpoint'))

delta_stream.withColumn('processed_data', col('processed_data').cast('string'))


delta_stream = delta_stream.withColumn("processed_data",
   concat_ws(",",col("processed_data")))

print(sink_output_path)
print(checkpoint_output)

delta_stream \
    .writeStream \
    .format("csv")\
    .option("format", "append")\
    .option("header","true")\
    .trigger(processingTime = "5 seconds")\
    .option("path", sink_output_path)\
    .option("checkpointLocation", checkpoint_output) \
    .outputMode("append") \
    .start()\
    .awaitTermination()



