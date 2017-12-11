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
    def __init__(self, config):
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
        
class Hexapod_12DOF(Hexapod):
    def __init__(self, config):
        super().__init__(config)
        
    def initial_tests(self, timestep=1):
        self.move_all_legs(raise_value=0, rotate_value=100)
        time.sleep(timestep)
        self.move_all_legs(raise_value=100, rotate_value=100)
        time.sleep(timestep)
        self.move_all_legs(raise_value=0, rotate_value=100)
    
    def sit(self):
        self.lower_height()

    def stand(self):
        self.center_height()

    def center_all_legs(self):
        pass

    def align_all_legs(self):
        pass

    def spread_all_legs(self):
        pass

    def lower_height(self):
        self.servos['right_front_raise'].set_position(0)
        self.servos['right_center_raise'].set_position(0)
        self.servos['right_back_raise'].set_position(0)
        self.servos['left_front_raise'].set_position(0)
        self.servos['left_center_raise'].set_position(0)
        self.servos['left_back_raise'].set_position(0)
        
    def center_height(self):
        self.servos['right_front_raise'].set_position(50)
        self.servos['right_center_raise'].set_position(50)
        self.servos['right_back_raise'].set_position(50)
        self.servos['left_front_raise'].set_position(50)
        self.servos['left_center_raise'].set_position(50)
        self.servos['left_back_raise'].set_position(50)
        
    def raise_height(self):
        self.servos['right_front_raise'].set_position(100)
        self.servos['right_center_raise'].set_position(100)
        self.servos['right_back_raise'].set_position(100)
        self.servos['left_front_raise'].set_position(100)
        self.servos['left_center_raise'].set_position(100)
        self.servos['left_back_raise'].set_position(100)
        
    def right_left_right_step(self, time_step=0.2):
        # Prep for a step (right-left-right step)
        self.servos['right_front_raise'].move_center()
        self.servos['right_center_raise'].move_center()
        self.servos['right_back_raise'].move_center()
        self.servos['left_front_raise'].move_center()
        self.servos['left_center_raise'].move_center()
        self.servos['left_back_raise'].move_center()

        time.sleep(time_step)

        # Raise 3 legs
        self.servos['right_front_raise'].move_up()
        self.servos['left_center_raise'].move_up()
        self.servos['right_back_raise'].move_up()

        time.sleep(time_step)

        # Rotate 3 legs forward
        self.servos['right_front_rotate'].move_forward()
        self.servos['left_center_rotate'].move_forward()
        self.servos['right_back_rotate'].move_forward()

        time.sleep(time_step)

        # Lower 3 legs
        self.servos['right_front_raise'].set_position(70)
        self.servos['left_center_raise'].set_position(70)
        self.servos['right_back_raise'].set_position(70)
        
        self.servos['left_front_raise'].move_up()
        self.servos['right_center_raise'].move_up()
        self.servos['left_back_raise'].move_up()

        time.sleep(time_step)

        # Rotate 3 legs back
        self.servos['right_front_rotate'].move_back()
        self.servos['left_center_rotate'].move_back()
        self.servos['right_back_rotate'].move_back()

        time.sleep(time_step)

        # Center 3 legs
        self.servos['right_front_raise'].move_center()
        self.servos['left_center_raise'].move_center()
        self.servos['right_back_raise'].move_center()
        self.servos['left_front_raise'].move_center()
        self.servos['right_center_raise'].move_center()
        self.servos['left_back_raise'].move_center()
    
    def left_right_left_step(self, time_step=0.2):
        # Prep for a step (left-right-left step)
        self.servos['right_front_raise'].move_center()
        self.servos['right_center_raise'].move_center()
        self.servos['right_back_raise'].move_center()
        self.servos['left_front_raise'].move_center()
        self.servos['left_center_raise'].move_center()
        self.servos['left_back_raise'].move_center()

        time.sleep(time_step)

        # Raise 3 legs
        self.servos['left_front_raise'].move_up()
        self.servos['right_center_raise'].move_up()
        self.servos['left_back_raise'].move_up()

        time.sleep(time_step)

        # Rotate 3 legs forward
        self.servos['left_front_rotate'].move_forward()
        self.servos['right_center_rotate'].move_forward()
        self.servos['left_back_rotate'].move_forward()

        time.sleep(time_step)

        # Lower 3 legs
        self.servos['left_front_raise'].set_position(70)
        self.servos['right_center_raise'].set_position(70)
        self.servos['left_back_raise'].set_position(70)
        
        self.servos['right_front_raise'].move_up()
        self.servos['left_center_raise'].move_up()
        self.servos['right_back_raise'].move_up()

        time.sleep(time_step)

        # Rotate 3 legs back
        self.servos['left_front_rotate'].move_back()
        self.servos['right_center_rotate'].move_back()
        self.servos['left_back_rotate'].move_back()

        time.sleep(time_step)

        # Center 3 legs
        self.servos['left_front_raise'].move_center()
        self.servos['right_center_raise'].move_center()
        self.servos['left_back_raise'].move_center()
        self.servos['right_front_raise'].move_center()
        self.servos['left_center_raise'].move_center()
        self.servos['right_back_raise'].move_center()
    
    def left_right_left_step_back(self, time_step=0.2):
        # Prep for a step (left-right-left step)
        self.servos['right_front_raise'].move_center()
        self.servos['right_center_raise'].move_center()
        self.servos['right_back_raise'].move_center()
        self.servos['left_front_raise'].move_center()
        self.servos['left_center_raise'].move_center()
        self.servos['left_back_raise'].move_center()

        time.sleep(time_step)

        # Lower 3 legs
        self.servos['left_front_raise'].set_position(70)
        self.servos['right_center_raise'].set_position(70)
        self.servos['left_back_raise'].set_position(70)

        time.sleep(time_step)

        # Rotate 3 legs back
        self.servos['left_front_rotate'].move_forward()
        self.servos['right_center_rotate'].move_forward()
        self.servos['left_back_rotate'].move_forward()

        time.sleep(time_step)

        # Raise 3 legs
        self.servos['left_front_raise'].move_up()
        self.servos['right_center_raise'].move_up()
        self.servos['left_back_raise'].move_up()

        time.sleep(time_step)

        # Rotate 3 legs back
        self.servos['left_front_rotate'].move_back()
        self.servos['right_center_rotate'].move_back()
        self.servos['left_back_rotate'].move_back()

        time.sleep(time_step)

        # Center 3 legs
        self.servos['left_front_raise'].move_center()
        self.servos['right_center_raise'].move_center()
        self.servos['left_back_raise'].move_center()

    def right_left_right_step_back(self, time_step=0.2):
        # Prep for a step (left-right-left step)
        self.servos['right_front_raise'].move_center()
        self.servos['right_center_raise'].move_center()
        self.servos['right_back_raise'].move_center()
        self.servos['left_front_raise'].move_center()
        self.servos['left_center_raise'].move_center()
        self.servos['left_back_raise'].move_center()

        time.sleep(time_step)

        # Lower 3 legs
        self.servos['right_front_raise'].set_position(70)
        self.servos['left_center_raise'].set_position(70)
        self.servos['right_back_raise'].set_position(70)

        time.sleep(time_step)

        # Rotate 3 legs back
        self.servos['right_front_rotate'].move_forward()
        self.servos['left_center_rotate'].move_forward()
        self.servos['right_back_rotate'].move_forward()

        time.sleep(time_step)

        # Raise 3 legs
        self.servos['right_front_raise'].move_up()
        self.servos['left_center_raise'].move_up()
        self.servos['right_back_raise'].move_up()

        time.sleep(time_step)

        # Rotate 3 legs back
        self.servos['right_front_rotate'].move_back()
        self.servos['left_center_rotate'].move_back()
        self.servos['right_back_rotate'].move_back()

        time.sleep(time_step)

        # Center 3 legs
        self.servos['right_front_raise'].move_center()
        self.servos['left_center_raise'].move_center()
        self.servos['right_back_raise'].move_center()
        
    def turn_left(self, time_step=0.2):
        # Raise right front/back legs
        self.servos['right_front_raise'].move_up()
        self.servos['right_back_raise'].move_up()

        time.sleep(time_step)

        # Rotate forward
        self.servos['right_front_rotate'].move_forward()
        self.servos['right_back_rotate'].move_forward()

        time.sleep(time_step)

        # Raise right front/back legs
        self.servos['right_front_raise'].set_position(90)
        self.servos['right_center_raise'].move_up()
        self.servos['right_back_raise'].set_position(90)

        time.sleep(time_step)

        # Rotate Center
        self.servos['right_front_rotate'].move_center()
        self.servos['right_back_rotate'].move_center()

        time.sleep(time_step)

        # Raise right front/back legs
        self.servos['right_front_raise'].move_center()
        self.servos['right_center_raise'].move_center()
        self.servos['right_back_raise'].move_center()
        
    def turn_right(self, time_step=0.2):
        # Raise left front/back legs
        self.servos['left_front_raise'].move_up()
        self.servos['left_back_raise'].move_up()

        time.sleep(time_step)

        # Rotate forward
        self.servos['left_front_rotate'].move_forward()
        self.servos['left_back_rotate'].move_forward()

        time.sleep(time_step)

        # Raise left front/back legs
        self.servos['left_front_raise'].set_position(90)
        self.servos['left_center_raise'].move_up()
        self.servos['left_back_raise'].set_position(90)

        time.sleep(time_step)

        # Rotate Center
        self.servos['left_front_rotate'].move_center()
        self.servos['left_back_rotate'].move_center()

        time.sleep(time_step)

        # Raise left front/back legs
        self.servos['left_front_raise'].move_center()
        self.servos['left_center_raise'].move_center()
        self.servos['left_back_raise'].move_center()

    def move_all_legs(self, rotate_value=None, raise_value=None):
        if rotate_value is not None:
            self.servos['right_front_rotate'].set_position(rotate_value)
            self.servos['right_center_rotate'].set_position(rotate_value)
            self.servos['right_back_rotate'].set_position(rotate_value)
            self.servos['left_front_rotate'].set_position(rotate_value)
            self.servos['left_center_rotate'].set_position(rotate_value)
            self.servos['left_back_rotate'].set_position(rotate_value)
            
        if raise_value is not None:
            self.servos['right_front_raise'].set_position(raise_value)
            self.servos['right_center_raise'].set_position(raise_value)
            self.servos['right_back_raise'].set_position(raise_value)
            self.servos['left_front_raise'].set_position(raise_value)
            self.servos['left_center_raise'].set_position(raise_value)
            self.servos['left_back_raise'].set_position(raise_value)
            
    def move_right_legs(self, rotate_value=None, raise_value=None):
        if rotate_value is not None:
            self.servos['right_front_rotate'].set_position(rotate_value)
            self.servos['right_center_rotate'].set_position(rotate_value)
            self.servos['right_back_rotate'].set_position(rotate_value)
            
        if raise_value is not None:
            self.servos['right_front_raise'].set_position(raise_value)
            self.servos['right_center_raise'].set_position(raise_value)
            self.servos['right_back_raise'].set_position(raise_value)

    def move_left_legs(self, rotate_value=None, raise_value=None):
        if rotate_value is not None:
            self.servos['left_front_rotate'].set_position(rotate_value)
            self.servos['left_center_rotate'].set_position(rotate_value)
            self.servos['left_back_rotate'].set_position(rotate_value)
            
        if raise_value is not None:
            self.servos['left_front_raise'].set_position(raise_value)
            self.servos['left_center_raise'].set_position(raise_value)
            self.servos['left_back_raise'].set_position(raise_value)            
            
    def move_front_legs(self, rotate_value=None, raise_value=None):
        if rotate_value is not None:
            self.servos['left_front_rotate'].set_position(rotate_value)
            self.servos['right_front_rotate'].set_position(rotate_value)
            
        if raise_value is not None:
            self.servos['left_front_raise'].set_position(raise_value)
            self.servos['right_front_raise'].set_position(raise_value)
    
    def move_center_legs(self, rotate_value=None, raise_value=None):
        if rotate_value is not None:
            self.servos['left_center_rotate'].set_position(rotate_value)
            self.servos['right_center_rotate'].set_position(rotate_value)
            
        if raise_value is not None:
            self.servos['left_center_raise'].set_position(raise_value)
            self.servos['right_center_raise'].set_position(raise_value)
            
    def move_back_legs(self, rotate_value=None, raise_value=None):
        if rotate_value is not None:
            self.servos['left_back_rotate'].set_position(rotate_value)
            self.servos['right_back_rotate'].set_position(rotate_value)
            
        if raise_value is not None:
            self.servos['left_back_raise'].set_position(raise_value)
            self.servos['right_back_raise'].set_position(raise_value)
            
    def reposition_front_legs(self, position, time_step=0.5):
        # Raise Legs and wiggle
        self.move_front_legs(raise_value=0)
        time.sleep(time_step)
        self.move_front_legs(rotate_value=position)
        time.sleep(time_step)
        self.move_front_legs(raise_value=50)
        
    def reposition_center_legs(self, position, time_step=0.5):
        # Raise Legs and wiggle
        self.move_center_legs(raise_value=0)
        time.sleep(time_step)
        self.move_center_legs(rotate_value=position)
        time.sleep(time_step)
        self.move_center_legs(raise_value=50)
        
    def reposition_back_legs(self, position, time_step=0.5):
        # Raise Legs and wiggle
        self.move_back_legs(raise_value=0)
        time.sleep(time_step)
        self.move_back_legs(rotate_value=position)
        time.sleep(time_step)
        self.move_back_legs(raise_value=50)
        
    def front_to_back_wave(self, time_step=0.2):
        self.servos['left_front_rotate'].move_back()
        self.servos['right_front_rotate'].move_back()

        time.sleep(time_step)

        self.servos['left_front_rotate'].move_forward()
        self.servos['right_front_rotate'].move_forward()

        time.sleep(time_step)
        
    def side_to_side_wave(self, time_step=0.2):
        self.servos['left_front_rotate'].move_forward()
        self.servos['right_front_rotate'].move_back()

        time.sleep(time_step)

        self.servos['left_front_rotate'].move_back()
        self.servos['right_front_rotate'].move_forward()

        time.sleep(time_step)
        
    def front_to_back_wave_back(self, time_step=0.2):
        self.servos['left_back_rotate'].move_back()
        self.servos['right_back_rotate'].move_back()

        time.sleep(time_step)

        self.servos['left_back_rotate'].move_forward()
        self.servos['right_back_rotate'].move_forward()

        time.sleep(time_step)
        
    def side_to_side_wave_back(self, time_step=0.2):
        self.servos['left_back_rotate'].move_forward()
        self.servos['right_back_rotate'].move_back()

        time.sleep(time_step)

        self.servos['left_back_rotate'].move_back()
        self.servos['right_back_rotate'].move_forward()

        time.sleep(time_step)
        
    def front_leg_dancing(self, step=1, time_step=0.5, iteration=4):
        self.reposition_center_legs(0)
        self.move_center_legs(raise_value=100)
        
        self.servos['left_center_raise'].move_down()
        self.servos['right_center_raise'].move_down()

        time.sleep(time_step)

        self.servos['left_front_raise'].move_up()
        self.servos['right_front_raise'].move_up()

        time.sleep(time_step)

        for i in range(iteration):
            if step == 1:
                self.side_to_side_wave(time_step)
            elif step == 2:
                self.front_to_back_wave(time_step)
            else:
                pass # not implemented yet!

        self.servos['left_front_rotate'].move_center()
        self.servos['right_front_rotate'].move_center()

        self.servos['left_center_raise'].move_center()
        self.servos['right_center_raise'].move_center()

        time.sleep(time_step)

        self.servos['left_front_raise'].move_center()
        self.servos['right_front_raise'].move_center()

        time.sleep(time_step)
        
        self.reposition_center_legs(100)
        
    def back_leg_dancing(self, step=1, time_step=0.5, iteration=4):
        self.reposition_center_legs(100)
        self.move_center_legs(raise_value=100)
        
        self.servos['left_center_raise'].move_down()
        self.servos['right_center_raise'].move_down()

        time.sleep(time_step)

        self.servos['left_back_raise'].move_up()
        self.servos['right_back_raise'].move_up()

        time.sleep(time_step)
        for i in range(iteration):
            if step == 1:
                self.side_to_side_wave_back(time_step)
            elif step == 2:
                self.front_to_back_wave_back(time_step)
            else:
                pass # not implemented yet!

        self.servos['left_back_rotate'].move_center()
        self.servos['right_back_rotate'].move_center()

        self.servos['left_center_raise'].move_center()
        self.servos['right_center_raise'].move_center()

        time.sleep(time_step)

        self.servos['left_back_raise'].move_center()
        self.servos['right_back_raise'].move_center()

        time.sleep(time_step)
        
        self.reposition_center_legs(100)
        
class Hexapod_18DOF(Hexapod):
    def __init__(self, config):
        super().__init__(config)   
        
    def initial_tests(self, iteration=1, timestep=1):
        # Setup initial state
        self.align_all_legs()
        self.resting_state()
        self.center_all_legs()
        time.sleep(timestep)

        for i in range(iteration):
            # Increase height
            self.short_from_resting_state()
            time.sleep(timestep)
            self.square_from_short_state()
            time.sleep(timestep)
            self.tall_state()
            time.sleep(timestep)

            # Decrease height
            self.square_from_tall_state()
            time.sleep(timestep)
            self.short_from_square_state()
            time.sleep(timestep)
            self.resting_state()
            time.sleep(timestep)
        
    def move_leg(self, name, rotate_value=None, lower_value=None, upper_value=None):
        if rotate_value is not None:
            self.servos[name + '_rotate'].set_position(rotate_value)

        if lower_value is not None:
            self.servos[name + '_lower'].set_position(lower_value)

        if upper_value is not None:
            self.servos[name + '_upper'].set_position(upper_value)
            
    def move_all_legs(self, rotate_value=None, lower_value=None, upper_value=None):
        self.move_leg('left_front', rotate_value=rotate_value, lower_value=lower_value, upper_value=upper_value)
        self.move_leg('left_center', rotate_value=rotate_value, lower_value=lower_value, upper_value=upper_value)
        self.move_leg('left_back', rotate_value=rotate_value, lower_value=lower_value, upper_value=upper_value)
        self.move_leg('right_front', rotate_value=rotate_value, lower_value=lower_value, upper_value=upper_value)
        self.move_leg('right_center', rotate_value=rotate_value, lower_value=lower_value, upper_value=upper_value)
        self.move_leg('right_back', rotate_value=rotate_value, lower_value=lower_value, upper_value=upper_value)
                
    def move_left_legs(self, rotate_value=None, lower_value=None, upper_value=None):
        self.move_leg('left_front', rotate_value=rotate_value, lower_value=lower_value, upper_value=upper_value)
        self.move_leg('left_center', rotate_value=rotate_value, lower_value=lower_value, upper_value=upper_value)
        self.move_leg('left_back', rotate_value=rotate_value, lower_value=lower_value, upper_value=upper_value)        
                
    def move_right_legs(self, rotate_value=None, lower_value=None, upper_value=None):
        self.move_leg('right_front', rotate_value=rotate_value, lower_value=lower_value, upper_value=upper_value)
        self.move_leg('right_center', rotate_value=rotate_value, lower_value=lower_value, upper_value=upper_value)
        self.move_leg('right_back', rotate_value=rotate_value, lower_value=lower_value, upper_value=upper_value)        
                
    def move_front_legs(self, rotate_value=None, lower_value=None, upper_value=None):
        self.move_leg('left_front', rotate_value=rotate_value, lower_value=lower_value, upper_value=upper_value)
        self.move_leg('right_front', rotate_value=rotate_value, lower_value=lower_value, upper_value=upper_value)        
                
    def move_center_legs(self, rotate_value=None, lower_value=None, upper_value=None):
        self.move_leg('left_center', rotate_value=rotate_value, lower_value=lower_value, upper_value=upper_value)
        self.move_leg('right_center', rotate_value=rotate_value, lower_value=lower_value, upper_value=upper_value)        
                
    def move_back_legs(self, rotate_value=None, lower_value=None, upper_value=None):
        self.move_leg('left_back', rotate_value=rotate_value, lower_value=lower_value, upper_value=upper_value)
        self.move_leg('right_back', rotate_value=rotate_value, lower_value=lower_value, upper_value=upper_value)

    def turn_right(self, backward=False, timestep=0.2):
        raise_height = 10
        resting_height = 20
        support_height = 25

        self.center_all_legs()
        self.stand()

        time.sleep(timestep)

        self.servos['right_front_lower'].set_position(raise_height)
        self.servos['left_center_lower'].set_position(raise_height)
        self.servos['right_back_lower'].set_position(raise_height)

        time.sleep(timestep)

        # Rotate 3 legs forward
        if backward:
            self.servos['right_front_rotate'].set_position(100)
            self.servos['right_back_rotate'].set_position(80)
        else:
            self.servos['right_front_rotate'].set_position(0)
            self.servos['right_back_rotate'].set_position(0)

        time.sleep(timestep)

        self.servos['right_front_lower'].set_position(support_height)
        self.servos['left_center_lower'].set_position(support_height)
        self.servos['right_back_lower'].set_position(support_height)

        time.sleep(timestep)

        self.servos['left_front_lower'].set_position(raise_height)
        self.servos['right_center_lower'].set_position(raise_height)
        self.servos['left_back_lower'].set_position(raise_height)
        time.sleep(timestep)

        self.servos['right_front_rotate'].set_position(50)
        self.servos['right_back_rotate'].set_position(50)

        time.sleep(timestep)

        self.stand()
        
    def turn_left(self, backward=False, timestep=0.2):
        raise_height = 10
        resting_height = 20
        support_height = 30

        self.center_all_legs()
        self.stand()

        time.sleep(timestep)

        self.servos['left_front_lower'].set_position(raise_height)
        self.servos['right_center_lower'].set_position(raise_height)
        self.servos['left_back_lower'].set_position(raise_height)

        time.sleep(timestep)

        # Rotate 3 legs forward
        if backward:
            self.servos['left_front_rotate'].set_position(100)
            self.servos['left_back_rotate'].set_position(80)
        else:
            self.servos['left_front_rotate'].set_position(0)
            self.servos['left_back_rotate'].set_position(0)

        time.sleep(timestep)

        self.servos['left_front_lower'].set_position(support_height)
        self.servos['right_center_lower'].set_position(support_height)
        self.servos['left_back_lower'].set_position(support_height)

        time.sleep(timestep)

        self.servos['right_front_lower'].set_position(raise_height)
        self.servos['left_center_lower'].set_position(raise_height)
        self.servos['right_back_lower'].set_position(raise_height)

        time.sleep(timestep)

        self.servos['left_front_rotate'].set_position(50)
        self.servos['left_back_rotate'].set_position(50)

        time.sleep(timestep)

        self.stand()
        
    def right_left_right_step(self, backward=False, timestep=0.2):
        raise_height = 10
        resting_height = 20
        support_height = 30

        self.align_all_legs()
        self.stand()

        time.sleep(timestep)

        self.servos['right_front_lower'].set_position(raise_height)
        self.servos['left_center_lower'].set_position(raise_height)
        self.servos['right_back_lower'].set_position(raise_height)

        time.sleep(timestep)

        # Rotate 3 legs forward
        if backward:
            self.servos['right_front_rotate'].set_position(100)
            self.servos['left_center_rotate'].set_position(100)
            self.servos['right_back_rotate'].set_position(50)
        else:
            self.servos['right_front_rotate'].set_position(50)
            self.servos['left_center_rotate'].set_position(0)
            self.servos['right_back_rotate'].set_position(0)

        time.sleep(timestep)

        self.servos['right_front_lower'].set_position(support_height)
        self.servos['left_center_lower'].set_position(support_height)
        self.servos['right_back_lower'].set_position(support_height)

        time.sleep(timestep)

        # self.servos['left_front_lower'].set_position(raise_height)
        # self.servos['right_center_lower'].set_position(raise_height)
        # self.servos['left_back_lower'].set_position(raise_height)

        # time.sleep(timestep)

        # Rotate 3 legs forward
        if backward:
            self.servos['right_front_rotate'].set_position(50)
            self.servos['left_center_rotate'].set_position(0)
            self.servos['right_back_rotate'].set_position(0)
        else:

            self.servos['right_front_rotate'].set_position(100)
            self.servos['left_center_rotate'].set_position(100)
            self.servos['right_back_rotate'].set_position(50)

        time.sleep(timestep)

        self.servos['right_front_lower'].set_position(raise_height)
        self.servos['left_center_lower'].set_position(raise_height)
        self.servos['right_back_lower'].set_position(raise_height)

        time.sleep(timestep)

        self.align_all_legs()
        self.stand()
        
    def right_left_right_step_back(self, timestep=0.2):
        self.right_left_right_step(backward=True, timestep=timestep)        
        
    def left_right_left_step_back(self, timestep=0.2):
        self.left_right_left_step(backward=True, timestep=timestep)
        
    def left_right_left_step(self, backward=False, timestep=0.2):
        raise_height = 10
        resting_height = 20
        support_height = 30

        self.align_all_legs()
        self.stand()

        time.sleep(timestep)

        self.servos['left_front_lower'].set_position(raise_height)
        self.servos['right_center_lower'].set_position(raise_height)
        self.servos['left_back_lower'].set_position(raise_height)

        time.sleep(timestep)

        # Rotate 3 legs forward
        if backward:
            self.servos['left_front_rotate'].set_position(100)
            self.servos['right_center_rotate'].set_position(100)
            self.servos['left_back_rotate'].set_position(50)
        else:
            self.servos['left_front_rotate'].set_position(50)
            self.servos['right_center_rotate'].set_position(0)
            self.servos['left_back_rotate'].set_position(0)

        time.sleep(timestep)

        self.servos['left_front_lower'].set_position(support_height)
        self.servos['right_center_lower'].set_position(support_height)
        self.servos['left_back_lower'].set_position(support_height)

        time.sleep(timestep)

        # self.servos['right_front_lower'].set_position(raise_height)
        # self.servos['left_center_lower'].set_position(raise_height)
        # self.servos['right_back_lower'].set_position(raise_height)

        # time.sleep(timestep)

        # Rotate 3 legs forward
        if backward:
            self.servos['left_front_rotate'].set_position(50)
            self.servos['right_center_rotate'].set_position(0)
            self.servos['left_back_rotate'].set_position(0)
        else:

            self.servos['left_front_rotate'].set_position(100)
            self.servos['right_center_rotate'].set_position(100)
            self.servos['left_back_rotate'].set_position(50)

        time.sleep(timestep)

        self.servos['left_front_lower'].set_position(raise_height)
        self.servos['right_center_lower'].set_position(raise_height)
        self.servos['left_back_lower'].set_position(raise_height)

        time.sleep(timestep)

        self.align_all_legs()
        self.stand()

    def front_leg_dancing(self, step=1, timestep=0.5, iteration=4):
        # Initial movement position
        self.center_all_legs()
        self.stand()

        time.sleep(timestep)

        # Move center legs for support
        self.move_center_legs(rotate_value=0, upper_value=60, lower_value=40)

        time.sleep(timestep)

        if step == 1:
            for i in range(iteration):
                # Move front legs to the right
                self.move_leg('left_front', rotate_value=0)
                self.move_leg('right_front', rotate_value=80)

                time.sleep(timestep)

                # Move front legs to the left
                self.move_leg('left_front', rotate_value=80)
                self.move_leg('right_front', rotate_value=0)

                time.sleep(timestep)
        elif step == 2:
            for i in range(iteration):
                # Move front legs to the front
                self.move_leg('left_front', rotate_value=0)
                self.move_leg('right_front', rotate_value=0)

                time.sleep(timestep)

                # Move front legs to the back
                self.move_leg('left_front', rotate_value=80)
                self.move_leg('right_front', rotate_value=80)

                time.sleep(timestep)
        else:
            pass # unsupported movement

        time.sleep(timestep)

        self.move_front_legs(rotate_value=50)
        self.move_center_legs(rotate_value=50)
        self.stand()

        time.sleep(timestep)        
        
    def back_leg_dancing(self, step=1, timestep=0.5, iteration=4):
        # Initial movement position
        self.center_all_legs()
        self.stand()

        time.sleep(timestep)

        # Move center legs for support
        self.move_center_legs(rotate_value=100, upper_value=60, lower_value=40)

        time.sleep(timestep)

        if step == 1:
            for i in range(iteration):
                # Move front legs to the right
                self.move_leg('left_back', rotate_value=0)
                self.move_leg('right_back', rotate_value=80)

                time.sleep(timestep)

                # Move front legs to the left
                self.move_leg('left_back', rotate_value=80)
                self.move_leg('right_back', rotate_value=0)

                time.sleep(timestep)
        elif step == 2:
            for i in range(iteration):
                # Move back legs to the front
                self.move_leg('left_back', rotate_value=0)
                self.move_leg('right_back', rotate_value=0)

                time.sleep(0.5)

                # Move back legs to the back
                self.move_leg('left_back', rotate_value=80)
                self.move_leg('right_back', rotate_value=80)

                time.sleep(0.5)
        else:
            pass # unsupported movement

        time.sleep(timestep)

        self.move_back_legs(rotate_value=50)
        self.move_center_legs(rotate_value=50)
        self.stand()

        time.sleep(timestep)
