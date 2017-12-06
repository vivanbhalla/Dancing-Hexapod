/*

Code for servo calibration
by eLab Peers (C) 2014.

Visit us at:
http://www.elabpeers.com

All rights reserved.

Wiring:
For the servo
1. Orange wire on servo to Pin 10
2. Brown wire to GND on Arduino board or both GND on Arduino board and power source
3. Red wire to 5V on Arduino board or + of the power source

Features:
1.  The servo moves to 90 degree.

*/

#include <Servo.h>

Servo myservo;

void setup()
{
  myservo.attach(10);
}

void loop()
{
  myservo.write(90); 
}
