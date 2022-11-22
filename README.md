# Sentiment Analysis on Real-Time Twitter Data.

A real time streaming ETL pipeline for Twitter data is implemented using Apache Kafka, Apache Spark and MongoDB database. Sentiment analysis is performed using Spark Machine Learning libraries on the streaming data, before being written to the database.

## Architecture:

![Image](https://github.com/madhavms/Twitter-Sentiment-Analyser/blob/main/Images/SystemArchitecture.jpg?raw=true)


## Usage:

### 1.Setting up Kafka Environment:

STEP 1: GET KAFKA
Download the latest Kafka release and extract it:

```
$ tar -xzf kafka_2.13-3.1.0.tgz

$ cd kafka_2.13-3.1.0 
```

STEP 2: START THE KAFKA ENVIRONMENT
NOTE: Your local environment must have Java 8+ installed.

Run the following commands in order to start all services in the correct order:

Start the ZooKeeper service
(Note: Soon, ZooKeeper will no longer be required by Apache Kafka.)
```
$ bin/zookeeper-server-start.sh config/zookeeper.properties
```

Open another terminal session and run:

Start the Kafka broker service:
```
$ bin/kafka-server-start.sh config/server.properties
```
Once all services have successfully launched, you will have a basic Kafka environment running and ready to use.

STEP 3: CREATE A TOPIC TO STORE YOUR EVENTS
Kafka is a distributed event streaming platform that lets you read, write, store, and process events (also called records or messages in the documentation) across many machines.

Example events are payment transactions, geolocation updates from mobile phones, shipping orders, sensor measurements from IoT devices or medical equipment, and much more. These events are organized and stored in topics. Very simplified, a topic is similar to a folder in a filesystem, and the events are the files in that folder.

So before you can write your first events, you must create a topic. Open another terminal session and run:
```
$ bin/kafka-topics.sh --create --topic twitterdata --bootstrap-server localhost:9092
```


### 2.Installing the python dependencies:
```
pip install -r requirements.txt
```

### 3.Running the python programs:

Once all the Kakfa servers are running the python applications can be executed in the below order:

#### Run the Kafka Producer to write to the Kafka topic:
```
python producer.py
```
#### Run the Kafka Consumer to consume data from Kafka and perform ML predictions using SparkML. The prediction results are stored to MongoDB cloud database.
```
python consumer.py
```


## ML Pipeline for Sentiment Analysis

Stanford's [Sentiment140]https://www.kaggle.com/kazanova/sentiment140 dataset was used to train an ML pipeline consisting of five stages. Spark ML libraries were used for creating the ML pipeline. 

![Image](https://github.com/madhavms/Twitter-Sentiment-Analyser/blob/main/Images/ML%20Pipeline.jpg)
