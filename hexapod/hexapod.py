from __future__ import division
import time

# Import the PCA9685 module.
import Adafruit_PCA9685

class Servo:
    def __init__(
        self,
        name,
        board,
        channel,
        servo_min,
        servo_max,
        forward=None,
        back=None,
        up=None,
        down=None,
        center=None,
        invert=False
    ):
        self.name = name
        self.board = board
        self.channel = channel
        self.servo_min = servo_min
        self.servo_max = servo_max
        self.forward = forward
        self.back = back
        self.up = up
        self.down = down
        self.center = center
        self.invert = invert
    
    def set_max(self, max_value):
        self.servo_max = max_value
    
    def set_min(self, min_value):
        self.servo_min = min_value
        
    def servo_percent_to_pulse(self, percent):
        if 0 <= percent <= 100:
            if self.invert:
                percent = 100 - percent
                
            my_range = self.servo_max - self.servo_min
            offset = self.servo_min
            pulse = (percent * my_range)/100 + offset
        else:
            print('ERROR: percent must be between 0 and 100, got Percent = {}'.format(percent))
            print('Setting Percent = 0')
            pulse = 0
            
        return int(pulse)
    
    def set_position(self, percent):
        self.board.set_pwm(self.channel, 0, self.servo_percent_to_pulse(percent))
        
    # Low level function to tune min/max values
    def set_pulse(self, pulse):
        self.board.set_pwm(self.channel, 0, pulse)
        
    def set_center(self, percent):
        self.center = percent
        
    def set_forward(self, percent):
        self.forward = percent
        
    def set_back(self, percent):
        self.back = percent
        
    def set_up(self, percent):
        self.up = percent
        
    def set_down(self, percent):
        self.down = percent
            
    def move_forward(self):
        if self.forward is not None:
            self.set_position(self.forward)
        else:
            print('WARNING: forward not defined for servo: {}'.format(self.name))
        
    def move_back(self):
        if self.back is not None:
            self.set_position(self.back)  
        else:
            print('WARNING: back not defined for servo: {}'.format(self.name))

    def move_up(self):
        if self.up is not None:
            self.set_position(self.up)
        else:
            print('WARNING: up not defined for servo: {}'.format(self.name))
        
    def move_down(self):
        if self.down is not None:
            self.set_position(self.down)
        else:
            print('WARNING: down not defined for servo: {}'.format(self.name))

    def move_center(self):
        if self.center is not None:
            self.set_position(self.center)
        else:
            print('WARNING: center not defined for servo: {}'.format(self.name))
    
    
class Hexapod:
    def __init__(
        self,
        config
    ):
        self.boards = {}
        self.servos = {}
        if 'boards' in config:
            for board in config['boards']:
                address = board['board_address']
                pwm_freq = board['pwm_freq']
                # print('Board Address: {}'.format(hex(address)))
                # print('PWM Frequency (Hz): {}'.format(pwm_freq))
                # print()
                
                self.boards[address] = {}
                self.boards[address]['object'] = Adafruit_PCA9685.PCA9685(address=address)
                self.boards[address]['pwm_freq'] = pwm_freq
                self.boards[address]['object'].set_pwm_freq(pwm_freq)
                
                if 'servos' in board:
                    for servo in board['servos']:
                        name = servo['name']
                        channel = servo['channel']
                        servo_min = servo['servo_min']
                        servo_max = servo['servo_max']
                        forward = servo['forward']
                        back = servo['back']
                        up = servo['up']
                        down = servo['down']
                        center = servo['center']
                        invert = servo['invert']

                        # print('Servo Name: {}'.format(name))
                        # print('Servo Channel: {}'.format(channel))
                        # print('Servo Min: {}'.format(servo_min))
                        # print('Servo Max: {}'.format(servo_max))
                        # print('Forward: {}%'.format(forward))
                        # print('Back: {}%'.format(back))
                        # print('Up: {}%'.format(up))
                        # print('Down: {}%'.format(down))
                        # print('Center: {}%'.format(center))
                        # print()

                        self.servos[name] = Servo(
                            name=name,
                            board=self.boards[address]['object'],
                            channel=channel,
                            servo_min=servo_min,
                            servo_max=servo_max,
                            forward=forward,
                            back=back,
                            up=up,
                            down=down,
                            center=center,
                            invert=invert
                        )
                else:
                    print('ERROR: No Servos found for the hexapod for board {}'.format(address))
                    
        else:
            print('ERROR: No boards found for the hexapod.')
            
    def center_all_legs(self):
        # - Center all rotation
        
        self.servos['left_front_rotate'].move_center()
        time.sleep(0.01)
        self.servos['right_front_rotate'].move_center()
        time.sleep(0.01)

        self.servos['left_center_rotate'].move_center()
        time.sleep(0.01)
        self.servos['right_center_rotate'].move_center()
        time.sleep(0.01)

        self.servos['left_back_rotate'].move_center()
        time.sleep(0.01)
        self.servos['right_back_rotate'].move_center()
        time.sleep(0.01)
        
    def spread_all_legs(self):
        # - Center all rotation
        
        self.servos['left_front_rotate'].move_forward()
        time.sleep(0.01)
        self.servos['right_front_rotate'].move_forward()
        time.sleep(0.01)

        self.servos['left_center_rotate'].move_center()
        time.sleep(0.01)
        self.servos['right_center_rotate'].move_center()
        time.sleep(0.01)

        self.servos['left_back_rotate'].move_back()
        time.sleep(0.01)
        self.servos['right_back_rotate'].move_back()
        time.sleep(0.01)
        
    def raise_all_lowers(self):
        # - Raise all lowers
        
        self.servos['left_front_lower'].move_up()
        time.sleep(0.1)
        self.servos['right_front_lower'].move_up()
        time.sleep(0.1)

        self.servos['left_center_lower'].move_up()
        time.sleep(0.1)
        self.servos['right_center_lower'].move_up()
        time.sleep(0.1)

        self.servos['left_back_lower'].move_up()
        time.sleep(0.1)
        self.servos['right_back_lower'].move_up()
        time.sleep(0.1)
        
    def raise_all_uppers(self):
        self.move_all_uppers(0)
        
    def center_all_lowers(self):        
        # - Center all lowers
        self.servos['left_front_lower'].move_center()
        time.sleep(0.1)
        self.servos['right_front_lower'].move_center()
        time.sleep(0.1)

        self.servos['left_center_lower'].move_center()
        time.sleep(0.1)
        self.servos['right_center_lower'].move_center()
        time.sleep(0.1)

        self.servos['left_back_lower'].move_center()
        time.sleep(0.1)
        self.servos['right_back_lower'].move_center()
        time.sleep(0.1)
        
    def center_all_uppers(self):
        self.move_all_uppers(50)
        
    def lower_all_lowers(self):
        # - Lower all lowers
        self.servos['left_front_lower'].move_down()
        time.sleep(0.1)
        self.servos['right_front_lower'].move_down()
        time.sleep(0.1)

        self.servos['left_center_lower'].move_down()
        time.sleep(0.1)
        self.servos['right_center_lower'].move_down()
        time.sleep(0.1)

        self.servos['left_back_lower'].move_down()
        time.sleep(0.1)
        self.servos['right_back_lower'].move_down()
        time.sleep(0.1)
        
    def lower_all_uppers(self):
        self.move_all_uppers(100)
        
    def move_all_lowers(self, position):
        # - Move all lowers
        self.servos['left_front_lower'].set_position(position)
        time.sleep(0.01)
        self.servos['right_front_lower'].set_position(position)
        time.sleep(0.01)

        self.servos['left_center_lower'].set_position(position)
        time.sleep(0.01)
        self.servos['right_center_lower'].set_position(position)
        time.sleep(0.01)

        self.servos['left_back_lower'].set_position(position)
        time.sleep(0.01)
        self.servos['right_back_lower'].set_position(position)
        time.sleep(0.01)
        
    def move_right_lowers(self, position):
        # - Move all lowers
        self.servos['right_front_lower'].set_position(position)
        time.sleep(0.01)

        self.servos['right_center_lower'].set_position(position)
        time.sleep(0.01)

        self.servos['right_back_lower'].set_position(position)
        time.sleep(0.01)
        
    def move_left_lowers(self, position):
        # - Move all lowers
        self.servos['left_front_lower'].set_position(position)
        time.sleep(0.01)

        self.servos['left_center_lower'].set_position(position)
        time.sleep(0.01)

        self.servos['left_back_lower'].set_position(position)
        time.sleep(0.01)
                
    def move_right_left_right_lowers(self, position):
        # - Move all lowers
        self.servos['right_front_lower'].set_position(position)
        time.sleep(0.01)

        self.servos['left_center_lower'].set_position(position)
        time.sleep(0.01)

        self.servos['right_back_lower'].set_position(position)
        time.sleep(0.01)
            
    def move_left_right_left_lowers(self, position):
        # - Move all lowers
        self.servos['left_front_lower'].set_position(position)
        time.sleep(0.01)

        self.servos['right_center_lower'].set_position(position)
        time.sleep(0.01)

        self.servos['left_back_lower'].set_position(position)
        time.sleep(0.01)
        
    def move_all_uppers(self, position):
        # - Move all uppers
        self.servos['left_front_upper'].set_position(position)
        time.sleep(0.01)
        self.servos['right_front_upper'].set_position(position)
        time.sleep(0.01)

        self.servos['left_center_upper'].set_position(position)
        time.sleep(0.01)
        self.servos['right_center_upper'].set_position(position)
        time.sleep(0.01)

        self.servos['left_back_upper'].set_position(position)
        time.sleep(0.01)
        self.servos['right_back_upper'].set_position(position)
        time.sleep(0.01)
        
    def move_right_uppers(self, position):
        # - Move all lowers
        self.servos['right_front_upper'].set_position(position)
        time.sleep(0.01)

        self.servos['right_center_upper'].set_position(position)
        time.sleep(0.01)

        self.servos['right_back_upper'].set_position(position)
        time.sleep(0.01)
        
    def move_left_uppers(self, position):
        # - Move all lowers
        self.servos['left_front_upper'].set_position(position)
        time.sleep(0.01)

        self.servos['left_center_upper'].set_position(position)
        time.sleep(0.01)

        self.servos['left_back_upper'].set_position(position)
        time.sleep(0.01)
        
    def move_left_right_left_uppers(self, position):
        # - Move all lowers
        self.servos['left_front_upper'].set_position(position)
        time.sleep(0.01)

        self.servos['right_center_upper'].set_position(position)
        time.sleep(0.01)

        self.servos['left_back_upper'].set_position(position)
        time.sleep(0.01)
        
    def move_right_left_right_uppers(self, position):
        # - Move all lowers
        self.servos['right_front_upper'].set_position(position)
        time.sleep(0.01)

        self.servos['left_center_upper'].set_position(position)
        time.sleep(0.01)

        self.servos['right_back_upper'].set_position(position)
        time.sleep(0.01)