#################################################################################################
# Made by: Vivan Bhalla
# Description: This program is used to detect the object using its color as a parameter 
#################################################################################################

### Import the libraries ####
import numpy as np
import cv2

## Create a video capture object
cap = cv2.VideoCapture(0) # Send 0 since we have only one camera. Send 1 to use second camera

## Check whether capture object is opened or not
if(cap.isOpened() == False):
	## If object is not initialized then open it
	cap.open()

############################ TODO ######################################
## TODO: Remove the trackbars once HSV for the hexapod is configured
# Function to be called when trackbars change
def nothing(x):
	pass # IT simply does nothing

# Create a window
cv2.namedWindow('image')
# Create trackbars to select boundary values
cv2.createTrackbar('High H','image',0,179,nothing)
cv2.createTrackbar('High S','image',0,255,nothing)
cv2.createTrackbar('High V','image',0,255,nothing)
cv2.createTrackbar('Low H','image',0,179,nothing)
cv2.createTrackbar('Low S','image',0,255,nothing)
cv2.createTrackbar('Low V','image',0,255,nothing)

############################ TODO ######################################

## Start capturing frame by frame in an infinite loop
while(True): 

	# Start capturing the frames
	ret, frame = cap.read() # Get the returned value(T/F) and the frame.

	if(ret != True): # Check if reading was successful or not
		print("Cannot read from the frame\n")

	############################ TODO ######################################

	# Get the current position of the trackbars
	high_h = cv2.getTrackbarPos('High H','image')
	high_s = cv2.getTrackbarPos('High S','image')
	high_v = cv2.getTrackbarPos('High V','image')
	low_h = cv2.getTrackbarPos('Low H','image')
	low_s = cv2.getTrackbarPos('Low H','image')
	low_v = cv2.getTrackbarPos('Low H','image')

	# Create numpy arrays of these boundaries
	# TODO: hardcode the values below from what is found through experiment
	higher_boundary = np.array([high_h,high_s,high_v])
	lower_boundary = np.array([low_h,low_s,low_v])

	############################ TODO ######################################

	# Convert the captured frame from BGR to HSV format
	hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV) 

	# Threshold the HSV image to get only our object
	threshold = cv2.inRange(hsv,lower_boundary,higher_boundary)

	# Get the targeted image by doing bitwise and
	target = cv2.bitwise_and(frame,frame,mask=threshold)

	## Perform morphological transformations #####
	## Morphological opening
	# We first remove the white noise from the boundaries of the detected object - Erode operation
	# We create an elliptical kernel for the erosion
	target = cv2.erode(target,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)))

	# Perform the dilation to get the more enchanced image of the object
	target = cv2.dilate(target,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)))

	## Morphological Closing - This is done to fill holes insie the detected object. 
	## This is done by first dilation then eroding the image

	target = cv2.dilate(target,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)))
	target = cv2.erode(target,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)))

	## Display the images
	cv2.imshow("Result",target)
	cv2.imshow("Mask",threshold)
	cv2.imshow("Original Image",frame)
	k = cv2.waitKey(5) & 0xFF
	if k == 27:
		break



# Release the capture
cap.release()
cv2.destroyAllWindows()


