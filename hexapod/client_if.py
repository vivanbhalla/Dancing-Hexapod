import argparse
import socket
 
def get_args():
    parser = argparse.ArgumentParser(description='hexapod client.')

    parser.add_argument(
            '--host',
            default='192.168.0.102',
            help='host ip of the hexapod')

    parser.add_argument(
            '--port',
            default=5000,
            type=int,
            help='port used to communicate to the hexapod')

    return parser.parse_args()

def Main(host, port):
        mySocket = socket.socket()
        mySocket.connect((host,port))
         
        message = input(" -> ")
         
        while message != 'q':
            if message:
                mySocket.send(message.encode())
                data = mySocket.recv(1024).decode()
                 
                print ('Received from server: ' + data)
                 
            message = input(" -> ")
                 
        mySocket.close()
 
if __name__ == '__main__':
    args = get_args()

    print('Host: {}'.format(args.host))
    print('Port: {}'.format(args.port))

    Main(args.host, args.port)
