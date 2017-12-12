#################################################################################################
# Made by: Vivan Bhalla
# Description: This program is used to detect the object using its color as a parameter
#################################################################################################

### Import the libraries ####
import cv2
import math
import numpy as np

## HSV constants for robot and spotlight
# For yellow 12DOF hexapod
H_robot=29
S_robot=255
V_robot=255

H_robot_low=19
S_robot_low=0
V_robot_low=0

# For black 18DOF hexapod
# H_robot=179
# S_robot=255
# V_robot=42
# H_robot_low=0
# S_robot_low=0
# V_robot_low=0

H_spotlight=179
S_spotlight=255
V_spotlight=243

H_spotlight_low=0
S_spotlight_low=0
V_spotlight_low=0

def get_distance(threshold_robot, threshold_spotlight):
    ######################## Object Tracking #########################################################
    # We use the moments method to track the object

    # Convert the images to black and white

    # Get the moments of the two images
    moments_robot = cv2.moments(threshold_robot, binaryImage=False)
    moments_spotlight = cv2.moments(threshold_spotlight, binaryImage=False)

    # Calculate the area of the robot object
    area_robot=moments_robot["m00"]
    area_spotlight=moments_spotlight["m00"]

    X_r = np.NaN
    Y_r = np.NaN
    X_s = np.NaN
    Y_s = np.NaN

    # To remove the effect of noise, consider tracking above only a threshold of area
    if(area_robot > 10000):
        # Calculate the x and y coordinates of center
        X_r = int(moments_robot["m10"] / area_robot)
        Y_r = int(moments_robot["m01"] / area_robot)

    if(area_spotlight>8000):
        # Calculate the centre for spotlight
        X_s=int(moments_spotlight["m10"] / area_spotlight)
        Y_s=int(moments_spotlight["m01"] / area_spotlight)

    X_dist = X_r - X_s
    Y_dist = Y_r - Y_s

    # print('hexapod: ({},{})'.format(X_r, Y_r))
    # print('spotlight: ({}, {})'.format(X_s, Y_s))
    # print('distance: ({}, {})'.format(X_dist, Y_dist))
    # print()

    return((X_r, Y_r), (X_s, Y_s), (X_dist, Y_dist))

def initialize_camera():
    ## Create a video capture object
    cap = cv2.VideoCapture(0) # Send 0 since we have only one camera. Send 1 to use second camera

    ## Check whether capture object is opened or not
    if(cap.isOpened() == False):
        ## If object is not initialized then open it
        cap.open()

    return cap

def get_threshold_image(frame, H_low, H_high, S_low, S_high, V_low, V_high):
    higher_boundary = np.array([H_high, S_high, V_high])
    lower_boundary = np.array([H_low, S_low, V_low])

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    threshold = cv2.inRange(hsv, lower_boundary, higher_boundary)

    return threshold

def get_threshold_images(frame,
            H_robot_low, H_robot,
            S_robot_low, S_robot,
            V_robot_low, V_robot,
            H_spotlight_low, H_spotlight,
            S_spotlight_low, S_spotlight,
            V_spotlight_low, V_spotlight
        ):
    threshold_robot = get_threshold_image(frame,
            H_robot_low, H_robot,
            S_robot_low, S_robot,
            V_robot_low, V_robot)

    threshold_spotlight = get_threshold_image(frame,
            H_spotlight_low, H_spotlight,
            S_spotlight_low, S_spotlight,
            V_spotlight_low, V_spotlight)

    # invert the target_spotlight mask (spotlight is in black with white background, not white with black background...
    threshold_spotlight = cv2.bitwise_not(threshold_spotlight)

    return (threshold_robot, threshold_spotlight)

def clean_threshold_image(threshold):
    ## Perform morphological transformations #####
    ## Morphological opening
    # We first remove the white noise from the boundaries of the detected object - Erode operation
    # We create an elliptical kernel for the erosion
    threshold = cv2.erode(threshold,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)))

    # Perform the dilation to get the more enchanced image of the object
    threshold = cv2.dilate(threshold,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)))

    ## Morphological Closing - This is done to fill holes insie the detected object.
    ## This is done by first dilation then eroding the image
    threshold = cv2.dilate(threshold,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)))
    threshold = cv2.erode(threshold,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)))

    return threshold

def print_position_data(X_r, Y_r, X_s, Y_s, X_dist, Y_dist):
    print("Hexapod:\t({}, {})".format(X_r, Y_r))
    print("Spotlight:\t({}, {})".format(X_s, Y_s))
    print("Distance:\t({}, {})".format(X_dist, Y_dist))
    print()

def move_hexapod(mySocket, X_dist, Y_dist, found_x, found_y, count):
    # Find Y coordinates first
    if found_y == False:
        if Y_dist > 50:
            command = 'walk 2'
        elif Y_dist > 20:
            command = 'walk'
        elif Y_dist < -50:
            command = 'walk_back 2'
        elif Y_dist < -20:
            command = 'walk_back'
        else:
            # Then rotate to find X coordinates
            if X_dist > 0:
                command = 'rotate_left 10'
            elif X_dist < 0:
                command = 'rotate_right 10'

            found_y = True
    else:
        if found_x == False:
            if X_dist > 50:
                command = 'walk 2'
            elif X_dist > 20:
                command = 'walk'
            elif X_dist < -50:
                command = 'walk_back 2'
            elif X_dist < -20:
                command = 'walk_back'
            else:
                # The rotate back to Y coordinate
                if Y_dist > 0:
                    command = 'rotate_left 10'
                elif Y_dist < 0:
                    command = 'rotate_right 10'

                found_x = True
        else:
            # if both x and y are found, then dance!
            if count%2:
                command = 'front_dancing_1 4'
            else:
                command = 'back_dancing_1 4'

    # Update counter for dance moves
    if count > 10:
        count = 0
    count += 1

    mySocket.send(command.encode())
    data = mySocket.recv(1024).decode()

    return(('Recieved from server: {}'.format(data)), found_x, found_y, count)

def Main(mySocket=None):
    cap = initialize_camera()

    # counter to limit display output
    count = 0
    dance_count = 0
    found_y = False
    found_x = False

    ## Start capturing frame by frame in an infinite loop
    while(True):

        # Start capturing the frames
        ret, frame = cap.read() # Get the returned value(T/F) and the frame.

        if(ret != True): # Check if reading was successful or not
            print("Cannot read from the frame\n")


        (threshold_robot, threshold_spotlight) = get_threshold_images(
                frame,
                H_robot_low, H_robot,
                S_robot_low, S_robot,
                V_robot_low, V_robot,
                H_spotlight_low, H_spotlight,
                S_spotlight_low, S_spotlight,
                V_spotlight_low, V_spotlight)

        threshold_robot = clean_threshold_image(threshold_robot)
        threshold_spotlight = clean_threshold_image(threshold_spotlight)

        (X_r, Y_r), (X_s, Y_s), (X_dist, Y_dist) = get_distance(threshold_robot, threshold_spotlight)

        if count == 30:
            if mySocket:
                (ret, found_x, found_y, dance_count) = move_hexapod(mySocket, X_dist, Y_dist, found_x, found_y, dance_count)
                print(ret)

            print_position_data(X_r, Y_r, X_s, Y_s, X_dist, Y_dist)
            count = 0
        count += 1

        # Add dots to represent the location of the robot and spotlight on initial image
        if not math.isnan(X_r) and not math.isnan(Y_r):
            cv2.circle(frame, (int(X_r), int(Y_r)), 5, (0,0,255), -1)

        if not math.isnan(X_s) and not math.isnan(Y_s):
            cv2.circle(frame, (int(X_s), int(Y_s)), 5, (255,0,0), -1)

        ## Display the images
        # cv2.imshow("Mask_robot",threshold_robot)
        # cv2.imshow("Mask_spotlight",threshold_spotlight)
        cv2.imshow("Original Image",frame)
        k = cv2.waitKey(5) & 0xFF
        if k == 27:
            break

    # Release the capture
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    Main()
