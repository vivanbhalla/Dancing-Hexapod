#################################################################################################
# Made by: Vivan Bhalla
# Description: This program is used to detect the object using its color as a parameter 
#################################################################################################

### Import the libraries ####
import numpy as np
import cv2

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


## Create a video capture object
cap = cv2.VideoCapture(0) # Send 0 since we have only one camera. Send 1 to use second camera

## Check whether capture object is opened or not
if(cap.isOpened() == False):
    ## If object is not initialized then open it
    cap.open()

# Create a window
# cv2.namedWindow('image')

# counter to limit display output
count = 0

## Start capturing frame by frame in an infinite loop
while(True): 

    # Start capturing the frames
    ret, frame = cap.read() # Get the returned value(T/F) and the frame.

    if(ret != True): # Check if reading was successful or not
        print("Cannot read from the frame\n")

    # Create numpy arrays of these boundaries
    # TODO: hardcode the values below from what is found through experiment
    higher_boundary_robot = np.array([H_robot,S_robot,V_robot])
    lower_boundary_robot = np.array([H_robot_low,S_robot_low,V_robot_low])
    higher_boundary_spotlight = np.array([H_spotlight,S_spotlight,V_spotlight])
    lower_boundary_spotlight = np.array([H_spotlight_low,S_spotlight_low,V_spotlight_low])

    ############################ TODO ######################################

    # Convert the captured frame from BGR to HSV format
    hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV) 

    # Threshold the HSV image to get only our object
    threshold_robot = cv2.inRange(hsv,lower_boundary_robot,higher_boundary_robot)
    threshold_spotlight = cv2.inRange(hsv,lower_boundary_spotlight,higher_boundary_spotlight)

    # invert the target_spotlight mask (spotlight is in black with white background, not white with black background...
    threshold_spotlight = cv2.bitwise_not(threshold_spotlight)

    ## Perform morphological transformations #####
    ## Morphological opening
    # We first remove the white noise from the boundaries of the detected object - Erode operation
    # We create an elliptical kernel for the erosion
    threshold_robot = cv2.erode(threshold_robot,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)))
    threshold_spotlight = cv2.erode(threshold_spotlight,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)))

    # Perform the dilation to get the more enchanced image of the object
    threshold_robot = cv2.dilate(threshold_robot,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)))
    threshold_spotlight = cv2.dilate(threshold_spotlight,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)))

    ## Morphological Closing - This is done to fill holes insie the detected object. 
    ## This is done by first dilation then eroding the image
    threshold_robot = cv2.dilate(threshold_robot,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)))
    threshold_robot = cv2.erode(threshold_robot,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)))
    threshold_spotlight = cv2.dilate(threshold_spotlight,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)))
    threshold_spotlight = cv2.erode(threshold_spotlight,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)))

    ######################## Object Tracking #########################################################
    # We use the moments method to track the object

    # Convert the images to black and white

    # Get the moments of the two images
    moments_robot = cv2.moments(threshold_robot)
    moments_spotlight = cv2.moments(threshold_spotlight)

    # Calculate the area of the robot object
    area_robot=moments_robot["m00"]
    area_spotlight=moments_spotlight["m00"]

    # To remove the effect of noise, consider tracking above only a threshold of area
    if(area_robot > 10000):
        # Calculate the x and y coordinates of center
        X_r = moments_robot["m10"] / area_robot;
        Y_r = moments_robot["m01"] / area_robot

    if(area_spotlight>8000):
        # Calculate the centre for spotlight
        X_s=moments_spotlight["m10"] / area_spotlight
        Y_s=moments_spotlight["m01"] / area_spotlight

    if count > 100:
        if X_r and Y_r:
            print("Hexapod: {}, {}".format(X_r, Y_r))
        if X_s and Y_s:
            print("Spotlight: {}, {}".format(X_s, Y_s))
        print()
        count = 0
    count += 1

    # Add dots to represent the location of the robot and spotlight on initial image
    cv2.circle(frame, (int(X_r), int(Y_r)), 5, (0,0,255), -1) 
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
