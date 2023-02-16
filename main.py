from neopixel import Neopixel
import utime
from machine import Pin
from ds1302 import DS1302

ds = DS1302(Pin(18),Pin(17),Pin(16))
#ds.date_time([2023, 2, 8, 0, 22, 31, 0, 0]) # set datetime.
#ds.date_time() # returns the current datetime.


numpix = 16
strip = Neopixel(numpix, 0, 22, "GRB")
red = (255, 0, 0)
white = (255, 255, 255)
blue = (0,0,50)
strip.brightness(100)


blank = (0,0,0)


def one(x):
    for i in range(0,2):
        if x == 1:
            strip.set_pixel(i, white)
    
def two(x):
    for i in range(2,4):
        if x == 1:
            strip.set_pixel(i, white)

def four(x):
    for i in range(4,6):
        if x == 1:
            strip.set_pixel(i, white)

def eight(x):
    for i in range(6,8):
        if x == 1:
            strip.set_pixel(i, white)

def sixteen(x):
    for i in range(8,10):
        if x == 1:
            strip.set_pixel(i, white)

def thirtytwo(x):
    for i in range(10,12):
        if x == 1:
            strip.set_pixel(i, white)

def sixtyfour(x):
    for i in range(12,14):
        if x == 1:
            strip.set_pixel(i, white)

def onetwoeight(x):
    for i in range(14,16):
        if x == 1:
            strip.set_pixel(i, white)
            

def decToBinary(n):
    y = n
    for i in range(16):
        strip.set_pixel(i, red)    
    if y >= 128:
        onetwoeight(1)
        y = y - 128
    if y >= 64:
        sixtyfour(1)
        y = y - 64
    if y >= 32:
        thirtytwo(1)
        y = y - 32
    if y >= 16:
        sixteen(1)
        y = y - 16
    if y >= 8:
        eight(1)
        y = y - 8
    if y >= 4:
        four(1)
        y = y - 4
    if y >= 2:
        two(1)
        y = y - 2
    if y >= 1:
        one(1)
        y = y - 1

count = 0

#while count < 256:
    #decToBinary(count)
    #utime.sleep(1)  
    #count = count + 1
    #if count == 256:
        #count = 0
while True:
    print("hour: ",ds.hour())
    decToBinary(ds.hour())
    for i in range(10,16):
        strip.set_pixel(i, blue)
    strip.show()
    utime.sleep(5)
    print("minute: ",ds.minute())
    decToBinary(ds.minute())
    for i in range(12,16):
        strip.set_pixel(i, blue)
    strip.show()
    utime.sleep(10)
