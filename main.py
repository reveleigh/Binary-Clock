from machine import I2C, Pin
from Makerverse_RV3028 import Makerverse_RV3028
from neopixel import Neopixel
import utime

i2c = I2C(0, sda = Pin(0), scl = Pin(1))
rtc = Makerverse_RV3028(i2c = i2c)

# Setting the time with list format
# time = [10, 12, 3, 'AM'] # 10:12:03 AM, [HH:MM:SS 'AM/PM']
# date = [10, 11, 21] # 10th November, 2021, [DD MM YY]

# Setting the time with dictionary format
#date = {}
#date['day'] = 12
#date['month'] = 2
# Year can be "20xx" or "xx"
#date['year'] = 2023

#time = {}
#time['hour'] = 10
#time['min'] = 16
#time['sec'] = 0
# AM/PM indicator optional
# If omitted, time is assumed to be in 24-hr format
#time['ampm'] = 'PM' # or 'PM'

#rtc.setTime(time)
#rtc.setDate(date)
hour = rtc.getTime()[0]
mins = rtc.getTime()[1]
print("hour: ", hour, " mins: ", mins )

numpix = 64
strip = Neopixel(numpix, 0, 22, "GRB")
red = (255, 0, 0)

off = (0,0,0)

white = (255, 255, 255)
blue = (0,0,50)
strip.brightness(200)

for i in range(numpix):
    strip.set_pixel(i, off)
strip.show()


def one():
    for i in range(0,4):
        strip.set_pixel(i, white)
    for i in range(60,64):
        strip.set_pixel(i, white)
    
def two():
    for i in range(4,8):
        strip.set_pixel(i, white)
    for i in range(56,60):
        strip.set_pixel(i, white)

def four():
    for i in range(8,12):
        strip.set_pixel(i, white)
    for i in range(52,56):
        strip.set_pixel(i, white)

def eight():
    for i in range(12,16):
        strip.set_pixel(i, white)
    for i in range(48,52):
        strip.set_pixel(i, white)

def sixteen():
    for i in range(16,20):
        strip.set_pixel(i, white)
    for i in range(44,48):
        strip.set_pixel(i, white)

def thirtytwo():
    for i in range(20,24):
        strip.set_pixel(i, white)
    for i in range(40,44):
        strip.set_pixel(i, white)

def sixtyfour():
    for i in range(24,28):
        strip.set_pixel(i, white)
    for i in range(36,40):
        strip.set_pixel(i, white)

def onetwoeight():
    for i in range(28,32):
        strip.set_pixel(i, white)
    for i in range(32,36):
        strip.set_pixel(i, white)

def decToBinary(n):
    y = n   
    if y >= 128:
        onetwoeight()
        y = y - 128
    if y >= 64:
        sixtyfour()
        y = y - 64
    if y >= 32:
        thirtytwo()
        y = y - 32
    if y >= 16:
        sixteen()
        y = y - 16
    if y >= 8:
        eight()
        y = y - 8
    if y >= 4:
        four()
        y = y - 4
    if y >= 2:
        two()
        y = y - 2
    if y >= 1:
        one()
        y = y - 1



utime.sleep(5)

count = 0

clock = True
def showTime():
    #Set up hour
    for i in range(numpix):
        strip.set_pixel(i, red)     
    for i in range(16,38):
        strip.set_pixel(i, off)
    for i in range(32,48):
        strip.set_pixel(i, off)
    decToBinary(rtc.getTime()[0])
    strip.show()

    
    utime.sleep(5)
    
    #Set up minute
    for i in range(numpix):
        strip.set_pixel(i, red) 
    for i in range(24,32):
        strip.set_pixel(i, off)
    for i in range(32,40):
        strip.set_pixel(i, off)
    decToBinary(rtc.getTime()[1])
    strip.show()

    utime.sleep(10)

while clock:
    showTime()