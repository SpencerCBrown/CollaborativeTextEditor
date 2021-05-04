import pika
import sys
from threading import *

class Mailbox:
    def __init__(self, receive_callback, configPath):
        self.readConfig(configPath)
        self.callback = receive_callback
        self.setup_broadcast()
        self.thread = Thread(target = do_consuming, args=(self.channel,self.callback))

    def readConfig(self, configPath):
        f = open(configPath, "r")
        host = f.readlines()[0].rstrip('\n')
        rabbitMQHost = host

    def startListening(self):
        self.thread.start()

    # Producer
    def setup_broadcast(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost')
        )
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='messages', exchange_type='fanout')

    def broadcast_message(self, message):
        # print(message)
        self.channel.basic_publish(exchange='messages', routing_key='', body=message)
    
    def stop(self):
        self.connection.close()

# separate connection for this receiving thread
def do_consuming(channel, callback):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost')
    )
    channel = connection.channel()
    channel.exchange_declare(exchange='messages', exchange_type='fanout')
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange='messages', queue=queue_name)
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()
