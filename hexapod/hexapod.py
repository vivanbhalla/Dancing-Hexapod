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
        
        self.current_state = None
    
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
        pulse = self.servo_percent_to_pulse(percent)
        self.board.set_pwm(self.channel, 0, pulse)
        self.current_state = pulse
        
    # Low level function to tune min/max values
    def set_pulse(self, pulse):
        self.board.set_pwm(self.channel, 0, pulse)
        self.current_state = pulse
        
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

    def resting_state(self):
        self.move_all_uppers(100)
        time.sleep(0.02)
        self.move_all_lowers(0)
        
    def short_from_square_state(self):
        self.move_all_uppers(75)
        time.sleep(0.02)
        self.move_all_lowers(25)

    def short_from_resting_state(self):
        self.move_all_lowers(25)
        time.sleep(0.02)
        self.move_all_uppers(75)
        
    def square_from_tall_state(self):
        self.move_all_uppers(50)
        time.sleep(0.02)
        self.move_all_lowers(50)
        
    def square_from_short_state(self):
        self.move_all_lowers(50)
        time.sleep(0.02)
        self.move_all_uppers(50)
        
    def tall_state(self):
        self.move_all_lowers(75)
        time.sleep(0.02)
        self.move_all_uppers(25)
        
    def stand(self):
        self.short_from_resting_state()
    
    def sit(self):
        self.resting_state()

    def rotate(self, right=True):
        sleep_time = 0.5
        # Raise the center legs
        self.move_center_lowers(15)

        time.sleep(sleep_time)

        # position center legs for rotation
        if right:
            self.servos['left_center_rotate'].move_forward()
            self.servos['right_center_rotate'].move_back()
        else:
            self.servos['left_center_rotate'].move_back()
            self.servos['right_center_rotate'].move_forward()

        time.sleep(sleep_time)

        # Drop center legs to control rotation
        self.move_center_lowers(30)

        time.sleep(sleep_time)

        # position center legs for rotation
        if right:
            self.servos['left_center_rotate'].move_back()
            self.servos['right_center_rotate'].move_forward()
        else:
            self.servos['left_center_rotate'].move_forward()
            self.servos['right_center_rotate'].move_back()

        time.sleep(sleep_time)

        # raise the middle legs to re-center
        self.move_center_lowers(15)

        time.sleep(sleep_time)

        # center the middle legs
        self.move_center_rotators(50)

        time.sleep(sleep_time)

        # reset the center legs to prep for next movement
        self.move_center_lowers(25)        
        
    def row(self, forward=True):
        # forward = True
        sleep_time = 0.5

        # Raise the center legs
        self.move_center_lowers(15)

        time.sleep(sleep_time)

        # center the middle legs
        if forward:
            self.move_center_rotators(0)
        else:
            self.move_center_rotators(100)

        time.sleep(sleep_time)

        # plant legs for movement movement
        self.move_center_lowers(30)

        time.sleep(sleep_time)    

        # row the center legs
        if forward:
            self.move_center_rotators(100)
        else:
            self.move_center_rotators(0)

        time.sleep(sleep_time)

        # raise legs
        self.move_center_lowers(15)
        time.sleep(sleep_time)

        # center legs
        self.move_center_rotators(50)
        time.sleep(sleep_time)

        # reset legs
        self.move_center_lowers(25)
        
    def align_all_legs(self):
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

    def center_all_legs(self):
        self.move_back_rotators(50)
        self.move_center_rotators(50)
        self.move_front_rotators(50)
        
    def spread_all_legs(self):
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

    def move_front_rotators(self, position):
        self.servos['left_front_rotate'].set_position(position)
        time.sleep(0.01)
        self.servos['right_front_rotate'].set_position(position)
        time.sleep(0.01)

    def move_center_rotators(self, position):
        self.servos['left_center_rotate'].set_position(position)
        time.sleep(0.01)
        self.servos['right_center_rotate'].set_position(position)
        time.sleep(0.01)

    def move_back_rotators(self, position):
        self.servos['left_back_rotate'].set_position(position)
        time.sleep(0.01)
        self.servos['right_back_rotate'].set_position(position)
        time.sleep(0.01)
        
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
        
    def raise_all_lowers(self):
        self.move_all_lowers(0)
        
    def center_all_lowers(self):
        self.move_all_lowers(50)
        
    def lower_all_lowers(self):
        self.move_all_lowers(100)
       
    def move_front_lowers(self, position):
        self.servos['left_front_lower'].set_position(position)
        time.sleep(0.01)
        self.servos['right_front_lower'].set_position(position)
        time.sleep(0.01)
        
    def move_center_lowers(self, position):
        self.servos['left_center_lower'].set_position(position)
        time.sleep(0.01)
        self.servos['right_center_lower'].set_position(position)
        time.sleep(0.01)
        
    def move_back_lowers(self, position):
        self.servos['left_back_lower'].set_position(position)
        time.sleep(0.01)
        self.servos['right_back_lower'].set_position(position)
        time.sleep(0.01)
        
    def move_right_lowers(self, position):
        self.servos['right_front_lower'].set_position(position)
        time.sleep(0.01)

        self.servos['right_center_lower'].set_position(position)
        time.sleep(0.01)

        self.servos['right_back_lower'].set_position(position)
        time.sleep(0.01)
        
    def move_left_lowers(self, position):
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
        
    def raise_all_uppers(self):
        self.move_all_uppers(0)
    
    def center_all_uppers(self):
        self.move_all_uppers(50)
        
    def lower_all_uppers(self):
        self.move_all_uppers(100)

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
        
    def move_front_uppers(self, position):
        # - Move all uppers
        self.servos['left_front_upper'].set_position(position)
        time.sleep(0.01)
        self.servos['right_front_upper'].set_position(position)
        time.sleep(0.01)
        
    def move_center_uppers(self, position):
        self.servos['left_center_upper'].set_position(position)
        time.sleep(0.01)
        self.servos['right_center_upper'].set_position(position)
        time.sleep(0.01)
        
    def move_back_uppers(self, position):
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
        
    def raise_all_legs(self):
        self.raise_all_uppers()
        self.raise_all_lowers()