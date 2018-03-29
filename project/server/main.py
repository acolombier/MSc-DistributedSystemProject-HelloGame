import pika
from package.area import Area

        
if __name__ == "__main__":

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    
    a = [Area(i, channel) for i in range(0, 4)]
    a[0].run()
