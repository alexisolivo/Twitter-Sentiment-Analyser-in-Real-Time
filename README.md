#Sentiment Analysis on Real-Time Twitter Data.

A real time streaming ETL pipeline for Twitter data is implemented using Apache Kafka, Apache Spark and Delta Lake Database. Sentiment analysis is performed using Spark Machine Learning libraries on the streaming data, before being written to the database.

##Usage:

STEP 1: GET KAFKA
Download the latest Kafka release and extract it:

```
$ tar -xzf kafka_2.13-3.1.0.tgz

$ cd kafka_2.13-3.1.0 
```


STEP 2: START THE KAFKA ENVIRONMENT
NOTE: Your local environment must have Java 8+ installed.

Run the following commands in order to start all services in the correct order:

### Start the ZooKeeper service
### Note: Soon, ZooKeeper will no longer be required by Apache Kafka.
```
$ bin/zookeeper-server-start.sh config/zookeeper.properties
```

Open another terminal session and run:

### Start the Kafka broker service
$ bin/kafka-server-start.sh config/server.properties
Once all services have successfully launched, you will have a basic Kafka environment running and ready to use.

STEP 3: CREATE A TOPIC TO STORE YOUR EVENTS
Kafka is a distributed event streaming platform that lets you read, write, store, and process events (also called records or messages in the documentation) across many machines.

Example events are payment transactions, geolocation updates from mobile phones, shipping orders, sensor measurements from IoT devices or medical equipment, and much more. These events are organized and stored in topics. Very simplified, a topic is similar to a folder in a filesystem, and the events are the files in that folder.

So before you can write your first events, you must create a topic. Open another terminal session and run:
```
$ bin/kafka-topics.sh --create --topic twitterdata --bootstrap-server localhost:9092
```
All of Kafka's command line tools have additional options: run the kafka-topics.sh command without any arguments to display usage information. 

 For example, it can also show you details such as the partition count of the new topic:

```
$ bin/kafka-topics.sh --describe --topic twitterdata --bootstrap-server localhost:9092
```

Topic:twitterdata PartitionCount:1    ReplicationFactor:1 Configs:
    Topic: quickstart-events Partition: 0    Leader: 0   Replicas: 0 Isr: 0

Python Code
Installing Kafka API for Python:
So before we get started using Kafka in Python, we will need to install the Kafka library in Python. On your terminal run the following code:
```
pip3 install kafka
```

### Producer Module Code:
On your IDE, create a new Python module called producer. Here you can use your Tweepy’s on_data function with the KafkaProducer to feed the raw twitter data into your Kafka Cluster.

Install tweepy package:
```
pip install tweepy
```

```
In case of java error when starting spark, try switching to JAVA SDK 8
ie java version "1.8.0_202"

Steps for mac os: 

https://medium.com/@devkosal/switching-java-jdk-versions-on-macos-80bc868e686a
```
### Install virtualenv
virtualenv is a tool to create isolated Python projects. Think of it, as a cleanroom, isolated from other virsions of Python and libriries.

Enter this command into terminal:

```
sudo pip install virtualenv
```

or if you get an error
```
sudo -H pip install virtualenv
```

### Start virtualenv:
Navigate to where you want to store your code. Create new directory.
```
mkdir my_project && cd my_project
```
Inside my_project folder create a new virtualenv by typing the below command:
```
virtualenv env
```

Activate virtualenv
```
source env/bin/activate
```
