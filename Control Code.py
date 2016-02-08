import serial
import time
import pigpio

pin1=4    # front motor pin
pin2=18   # rear motor pin
inp=0     # string input converted to number
inc=50    # value of increment when 'l' or 'r' are sent
flag=0    # 1 means change inc, 0 means change speed
dir=1     # direction flag. 1 means forward, 0 means backwards

class motor:
	def __init__(self, pin, speed):
		self.pin = pin
		self.speed = speed
motor1=motor(pin1, 1210)   #front motor speed initialised at 1210 ms pulse width
motor2=motor(pin2, 1230)   #back motor speed initialised at 1230 ms pulse width
motors = []                #array of motors to be controlled
motors.append(motor1)
motors.append(motor2)

if pigpio.start(''): # must run notification test on localhost
    print("Connected to pigpio daemon.")

    #initialisation
    pigpio.set_mode(pin1, pigpio.OUTPUT)
    pigpio.set_mode(pin2, pigpio.OUTPUT)
    pigpio.set_PWM_range(pin1, 255)
    pigpio.set_PWM_range(pin2, 255)
    pigpio.set_PWM_frequency(pin1,50)
    pigpio.set_PWM_frequency(pin2,50)
    pigpio.set_servo_pulsewidth(pin1, 0)
    pigpio.set_servo_pulsewidth(pin2, 0)

    #open the serial port rfcomm1 defined in rfcomm.conf file
    ser = serial.Serial('/dev/rfcomm1',38400,timeout=.08)
    
    print ("\nConnected\n")
    ser.write('Connected')   #send message to the smartphone
    raw = ser.readline()

    while (raw != 'stop'):   #message 'stop' terminates the program
        raw = ser.readline()
        if (raw != ''):
            print(raw + '\n')
	    if (raw == 's'):  #stop both motors
		pigpio.set_servo_pulsewidth(motor1.pin, 0)
	        pigpio.set_servo_pulsewidth(motor2.pin, 0)
		ser.write('STOP')
	    if (raw == 'f'):  #'f' for forwards
                    
                #if previous direction was backwards
		#change to forward. 1500 ms is the neutral
		#pulse width.
		if (dir == 0):	
			motor1.speed = 2*1500 - motor1.speed
			motor2.speed = 2*1500 - motor2.speed
			dir = 1

		#set PWM signals to assigned speeds
		pigpio.set_servo_pulsewidth(motor1.pin, motor1.speed)
	        pigpio.set_servo_pulsewidth(motor2.pin, motor2.speed)
		ser.write('motor1 PWM = ' + str(motor1.speed))
		ser.write('motor2 PWM = ' + str(motor2.speed))
		
	    if (raw == 'b'):  #'b' for backwards

                #if previous direction was forward
                #change it to backwards.
		if (dir):
			motor1.speed = 2*1500 - motor1.speed
			motor2.speed = 2*1500 - motor2.speed
			dir = 0
		pigpio.set_servo_pulsewidth(motor1.pin, motor1.speed)
	        pigpio.set_servo_pulsewidth(motor2.pin, motor2.speed)
		ser.write('motor1 PWM = ' + str(motor1.speed))
		ser.write('motor2 PWM = ' + str(motor2.speed))
		
	    if (raw == 'r'):  #'r' means increment speed by inc
		for m in motors:
			m.speed = m.speed + inc
			pigpio.set_servo_pulsewidth(m.pin, m.speed)
			ser.write('PWM set to ' + str(m.speed))
			
	    if (raw == 'l'):  #'l' means decrement speed by inc
		for m in motors:
			m.speed = m.speed - inc
			pigpio.set_servo_pulsewidth(m.pin, m.speed)
			ser.write('PWM set to ' + str(m.speed))
			
	    elif (raw.isdigit()):  #if message is a digit
                inp=int(raw)       #convert the variable type to integer
		if (flag):         #change inc if flag is high
			if (inp>(-500) and inp<500):  #limit the value of inc
				inc=inp
				flag=0  #set inc change flag to low
				ser.write('inc = ' + str(inc))

		#if flag is low, change the servo speed
                elif (inp>200 and inp<2500):  #limit the value of servo speed
			for m in motors:
				m.speed = inp
				pigpio.set_servo_pulsewidth(m.pin, m.speed)
				ser.write('PWM set to ' + str(m.speed))

            #enable the change of inc value when a number is entered
	    elif (raw == 'inc'):
		flag=1

	    #set to control the speed of the rear servo only
	    #by leaving only motor2 in motors array.
	    elif (raw == 'back'):
		if (motor1 in motors):
			motors.remove(motor1)
		if (motor2 not in motors):
			motors.append(motor2)
		ser.write('motor2 (back) is controlled')

	    #set to control the speed of the front servo only
	    elif (raw == 'front'):
		if (motor1 not in motors):
			motors.append(motor1)
		if (motor2 in motors):
			motors.remove(motor2)
		ser.write('motor1 (front) is controlled')

	    #set to control the speed of both servos
	    elif (raw=='both'):
		if (motor1 not in motors):
			motors.append(motor1)
		if (motor2 not in motors):
			motors.append(motor2)
		ser.write('both motors are controlled')

    #termination of the program
    print("\nGOODBYE\n")
    ser.write('GOODBYE')
    pigpio.set_servo_pulsewidth(motor1.pin, 0)
    pigpio.set_servo_pulsewidth(motor2.pin, 0)
    ser.close()
    pigpio.stop()
else: print("pigpio did not start")
