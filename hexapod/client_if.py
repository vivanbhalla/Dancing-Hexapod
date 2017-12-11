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

    parser.add_argument(
            '-s',
            '--script',
            default=None,
            help='script file to run robot')

    return parser.parse_args()

def Main(host, port, script):
        mySocket = socket.socket()
        mySocket.connect((host,port))

        if script:
            with open(script) as f:
                for line in f:
                    mySocket.send(line.strip().encode())
                    data = mySocket.recv(1024).decode()

                    print('Recieved from server: ' + data)
                    
        else:
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
    print('Script: {}'.format(args.script))

    Main(args.host, args.port, args.script)

