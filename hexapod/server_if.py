import argparse
import socket
import time
import yaml

from hexapod import Hexapod_12DOF, Hexapod_18DOF
 
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
    my_hexapod = None
    
    # open config file
    with open(config_file) as f:
        my_config = yaml.load(f)

    if config_file == 'config_12DOF.yaml':
        my_hexapod = Hexapod_12DOF(my_config)
        my_hexapod.initial_tests()
        
    elif config_file == 'config_18DOF.yaml':
        my_hexapod = Hexapod_18DOF(my_config)
        my_hexapod.initial_tests()
        
    else:
        print('ERROR: Cannot recognize the config file!!!')

    return my_hexapod


def command_processor(data, my_hexapod):
    print('Data: {}'.format(data))

    items = data.split()
    if len(items) == 1:
        command = items[0]
        iteration = 1

    elif len(items) == 2:
        command = items[0]
        iteration = int(items[1])

    else:
        return 'ERROR: invalid command format'

    print('Command: {}'.format(command))
    print('Iteration: {}'.format(iteration))

    commands = [
        'turn_left',
        'turn_right',
        'walk_forward|walk',
        'walk_backward|walk_back',
        'front_dancing_1',
        'front_dancing_2',
        'back_dancing_1',
        'back_dancing_2',
        'sit',
        'stand',
        'center',
        'spread',
        'align',
        'rotate_left',
        'rotate_right',
    ]

    if command == 'turn_left':
        for i in range(iteration):
            print('turning left...')
            my_hexapod.turn_left()

        return ('Turning Left {} times'.format(iteration))

    elif command == 'turn_right':
        for i in range(iteration):
            print('turning right...')
            my_hexapod.turn_right()

        return ('Turning Right {} times'.format(iteration))

    elif command == 'rotate_left':
        for i in range(iteration):
            print('rotating left...')
            if i%2:
                my_hexapod.rotate(left=True, back=False)
            else:
                my_hexapod.rotate(left=True, back=True)

        return ('Rotating Left {} times'.format(iteration))

    elif command == 'rotate_right':
        for i in range(iteration):
            print('rotating_right...')
            if i%2:
                my_hexapod.rotate(left=False, back=False)
            else:
                my_hexapod.rotate(left=False, back=True)

        return ('Rotating Right {} times'.format(iteration))

    elif command == 'walk_forward' or command == 'walk':
        for i in range(iteration):
            print('walking forward...')
            if i%2:
                my_hexapod.left_right_left_step()
            else:
                my_hexapod.right_left_right_step()

        return ('Walking Forward {} times'.format(iteration))

    elif command == 'walk_backward' or command == 'walk_back':
        for i in range(iteration):
            print('walking backward...')
            if i%2:
                my_hexapod.left_right_left_step_back()
            else:
                my_hexapod.right_left_right_step_back()

        return ('Walking Backward {} times'.format(iteration))

    elif command == 'front_dancing_1':
        print('front dancing...')
        my_hexapod.front_leg_dancing(step=1, iteration=iteration)
        return ('Dancing Front Legs {} times'.format(iteration))

    elif command == 'front_dancing_2':
        print('front dancing...')
        my_hexapod.front_leg_dancing(step=2, iteration=iteration)
        return ('Dancing Front Legs {} times'.format(iteration))

    elif command == 'back_dancing_1':
        print('back dancing...')
        my_hexapod.back_leg_dancing(step=1, iteration=iteration)
        return ('Dancing Back Legs {} times'.format(iteration))

    elif command == 'back_dancing_2':
        print('back dancing...')
        my_hexapod.back_leg_dancing(step=2, iteration=iteration)
        return ('Dancing Back Legs {} times'.format(iteration))

    elif command == 'sit':
        print('sitting...')
        my_hexapod.sit()
        return ('Sitting')

    elif command == 'stand':
        print('standing...')
        my_hexapod.stand()
        return ('Standing')

    elif command == 'center':
        print('centering legs...')
        my_hexapod.center_all_legs()
        return ('Centering All Legs')

    elif command == 'align':
        print('aligning legs...')
        my_hexapod.align_all_legs()
        return ('Aligning All Legs')

    elif command == 'spread':
        print('spreading legs...')
        my_hexapod.spread_all_legs()
        return ('Spreading All Legs')

    elif command == 'commands':
        temp = 'Implemented Commands: '
        for command in commands:
            temp += command + ', '

        return temp

    else:
        print('ERROR: command not recognized: {}'.format(command))
        return 'Command not found!'

def listenToClient(client, address, my_hexapod):
    size=1024
    while True:
        try:
            data = client.recv(size).decode()
            if data:
                # Read command from client
                print("from connected user: " + str(data))
                response = command_processor(data, my_hexapod)

                # data = str(data).upper()
                client.send(response.encode())
            else:
                raise error('Client disconnected')
        except:
            client.close()
            return False

def Main(host, port, config_file):
    my_hexapod = initialize_hexapod(config_file)

    mySocket = socket.socket()
    mySocket.bind((host,port))
     
    mySocket.listen(5)
    while True:
        client, address = mySocket.accept()
        client.settimeout(300)
        print ("Connection from: " + str(address))
        listenToClient(client, address, my_hexapod)
     
if __name__ == '__main__':
    args = get_args()

    print('Host: {}'.format(args.host))
    print('Port: {}'.format(args.port))
    print('Config File: {}'.format(args.config_file))

    Main(args.host, args.port, args.config_file)
