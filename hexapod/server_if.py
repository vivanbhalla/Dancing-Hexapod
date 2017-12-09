import argparse
import socket
import time
import yaml

from hexapod import Hexapod_12DOF
 
def get_args():
    parser = argparse.ArgumentParser(description='hexapod server.')

    parser.add_argument(
            '--host',
            default='192.168.0.102',
            help='host ip of the hexapod')

    parser.add_argument(
            '--port',
            default=5000,
            type=int,
            help='port used to communicate to the hexapod')

    parser.add_argument(
            '-c',
            '--config_file',
            default='config_12DOF.yaml',
            help='hexapod configuration file')
    
    return parser.parse_args()

def initialize_hexapod(config_file):
    # open config file
    with open(config_file) as f:
        my_config = yaml.load(f)

    my_hexapod = Hexapod_12DOF(my_config)
    my_hexapod.move_all_legs(raise_value=0, rotate_value=100)
    time.sleep(1)
    my_hexapod.move_all_legs(raise_value=100, rotate_value=100)
    time.sleep(1)
    my_hexapod.move_all_legs(raise_value=0, rotate_value=100)

def listenToClient(client, address):
    size=1024
    while True:
        try:
            data = client.recv(size).decode()
            if data:
                # Read command from client
                print("from connected user: " + str(data))
                data = str(data).upper()
                client.send(data.encode())
            else:
                raise error('Client disconnected')
        except:
            client.close()
            return False

def Main(host, port, config_file):
    initialize_hexapod(config_file)

    mySocket = socket.socket()
    mySocket.bind((host,port))
     
    mySocket.listen(5)
    while True:
        client, address = mySocket.accept()
        client.settimeout(300)
        print ("Connection from: " + str(address))
        listenToClient(client, address)
     
if __name__ == '__main__':
    args = get_args()

    print('Host: {}'.format(args.host))
    print('Port: {}'.format(args.port))
    print('Config File: {}'.format(args.config_file))

    Main(args.host, args.port, args.config_file)
