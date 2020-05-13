from flask import Flask, redirect, render_template
from threading import Thread, Event
import RPi.GPIO as GPIO
import time
import sys
import serial 
import time
import SimpleMFRC522


app = Flask(__name__, static_folder='')
@app.route("/")
def hello():
    return render_template('newuser.html')

@app.route("/index")
def newuser2():
     
     return render_template('newuser2.html')

def initialize_rfid():
 reader = SimpleMFRC522.SimpleMFRC522()
 return reader

def read_rfid():
 reader = SimpleMFRC522.SimpleMFRC522()
 try:

       print("First, writing to the tag...")
       text = raw_input('Enter new data to write to tag, then hit Enter: ')
       name= text
       print("Place your tag next to the antenna to write")
       for i in range(1,6):
        reader.write_no_block(text)
       print("keep tag placed next to the antenna...")
       for i in range(1,6):   
        id, text= reader.read_no_block()
        if id != None:
          break
       print('You may now release the tag')

       if (id == None):
        print("No tag was scanned")
        return id

       else:

         readData = dict();
        # readData['id'] = readData['name'] 
         readData['id'] = str(id)
         readData['name'] = str(name)
         print(readData)
         print(readData['id'] )
         print(readData['name'] )
         


 finally:
        GPIO.cleanup()
        return readData

  #and need to return text inputed !

def detect_rfid():
 reader = SimpleMFRC522.SimpleMFRC522()
 start = time.time()
 end = start + 10
 
 while (time.time() <= end):       
  try:
        print("Now, reading tag - place it next to the antenna...")
        for i in range(1,6):   
         id= reader.read_id_no_block()
         if id != None:
          break
        print('You may now release the tag')

        
        if (id == None):
          print("no tag was read")
          return False 
  finally:
        GPIO.cleanup()

  return  str(id)


def initialize_gps():
  ser = serial.Serial ("/dev/ttyS0", 9600)
  return ser

def location(ser):
# this is the location checker for GPS
 current = time.time() # get current time
 timeout = 5
 endtime = current+timeout
 while current < endtime:
   current =  time.time()
   received_data = ser.readline()
   a = received_data.split(",")
   if a[0] == "$GNGGA":
                gpsData = {
                        "ts" : a[1],
                        "latitude" : a[2],
                        "latDir" : a[3],
                        "longitude" : a[4],
                        "longDir" : a[5],
                        "fix" : a[6]
                }
                if (int(gpsData['fix']) == 0): 
                  gpsData = {
                        "ts" : 0,
                        "latitude" : 0,
                        "latDir" : 0,
                        "longitude" : 0,
                        "longDir" : 0,
                        "fix" : 0
                }
                else:  
                 return gpsData
 return False


pin = 11                                              # BCM17 board11
GPIO.setmode(GPIO.BOARD)                              # Used BOARD numbering
GPIO.setup(pin, GPIO.OUT)                             # set pin to work in output mode

#home_lat = 40.7128 *100 #data that we have from gps
#home_lon = 74.0060 *100 #data that we have from gps

object_item = None             #erase this after you check id_list and name_list!!
#use to append function to add rfid tags
##APPEND THE id Here from KiFinder.read_rfid()
#id_list=[]
#name_list=[]


def radius():
 radius= (input("What is the radius? (in feet)"))                 #remember to convert!
 ##find cords feet ratio and use it  :::: 1 cord degree = 364,320 feet remember my degree is in the hundred's place
 #radius=  radius / 364320 * 100 #used the 100 for cause my cords are #### and not ##.##  
 #note 1 foot with my calculation is 0.00027448397 distance!!!
 return radius

left_home = Event()

def ledRadius(x):                                                  #when inside or outside the radius, x=0 or 1
 if (x==1):
  GPIO.output(pin, GPIO.HIGH)
 else:
  GPIO.output(pin, GPIO.LOW)
  

def homeLocation():
  gps = location(initialize_gps())
  if (gps):
     cords = dict();
     cords['home_lat'] = float(gps['latitude'])
     cords['home_lon'] = float(gps['longitude'])
     if (cords['home_lat'] == 0):
      print("There is no GPS signal, please try again")
     else:
      return cords


def read_GPS():

 homeCords=homeLocation()
 home_lat=homeCords['home_lat']
 home_lon=homeCords['home_lon']
 wasIAtHome = 0

 while True:

    gps = location(initialize_gps())

    if (gps): 
     lat = float(gps['latitude'])
     lon = float(gps['longitude'])
     #print("the lat is " + str(lat)+ "\n" +"vs home lat " + str(home_lat))            #just for testing
     #print("the long is " + str(lon)+ "\n"+"vs home long " + str(home_lon) )
     distanceHyp= ((home_lon - lon)**2 + (home_lat - lat)**2) ** .5                     #this is the distance a^2+b^2=c^2 
     print("Distance         Radius"+"\n" +str(distanceHyp)+"    " +str(radius))
     
     if (radius > distanceHyp):
       print("LED On")
       left_home.clear() 
       wasIAtHome = 1                                    #boolean for true
     
     elif (radius < distanceHyp) and (wasIAtHome == 1):
       wasIAtHome = 0;                                   #boolean for false 
       print("LED Off")
       left_home.set()                                   # check if outside radius
        
def enroll_object(object_item):
                                                    # use extend if adding more
      enrolled = read_rfid()
      print (enrolled)
      
      if enrolled == None:
        print("You have not enrolled an object, try again")
       # while enrolled == None:
        enrolled = read_rfid()
        print (enrolled)
    
     # if (len(object_item) > 0) :

      #  yes = {'yes','y', 'ye'}
       # no = {'no','n'}
       # answer =raw_input("You already have an enrolled item, do you want to replace it y/n?")
       # answer = answer.lower()
       # if answer in yes:
       #  object_item = enrolled
       # elif answer in no:
       #   print("You decided to keep your previous enrolled item: " + str(object_item))
       # else:
       #   print("Since you did not respond yes or no, the previous enrolled item is kept ")
       
      #print ("you have enrolled this object:  "+ str(enrolled))
      return object_item


def check_object(object_item):
  #for testing
  while True:
    left_home.wait()  
    start = time.time()

    while time.time() < start + 5:
     tag_val=detect_rfid();

    print(tag_val+" <-- This is this tag's ID ")    
    # turn LED off
    # do more stuff if left radius
    if (tag_val == object_item): #if it was already found dont count it PROBLEM can only check previous tag
      print("Found %s" % tag_val)
      print("Dont Buzz")
      left_home.clear()                                       
      
    else:
      print("buzzing")
      time.sleep(10)
      print("stopped buzzing")


if __name__ == "__main__":
 app.run(host='0.0.0.0', port=80, debug=True, threaded=True)
 initialize_gps()
 initialize_rfid()

 #KiFinder.read_rfid()

 radius = radius();
 


 object_item = enroll_object(object_item)        
                            



 gps_thread = Thread(target=read_GPS)
 check_thread = Thread(target=check_object, args=[object_item])  #make the arg id_list 

 gps_thread.start()
 check_thread.start()
 #app.run(host='0.0.0.0', port=80, debug=True, threaded=True)

 gps_thread.join()
 check_thread.join()

