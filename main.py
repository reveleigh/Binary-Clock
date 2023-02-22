from machine import I2C, Pin
from Makerverse_RV3028 import Makerverse_RV3028
from neopixel import Neopixel
import utime
import time

# Creating I2C instance and RTC object
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
#time['hour'] = 8
#time['min'] = 43
#time['sec'] = 0
# AM/PM indicator optional
# If omitted, time is assumed to be in 24-hr format
#time['ampm'] = 'PM' # or 'PM'

#rtc.setTime(time)
#rtc.setDate(date)

# Getting current hour and minute from RTC
hour = rtc.getTime()[0]
mins = rtc.getTime()[1]
print("hour: ", hour, " mins: ", mins )

# Setting up Neopixel object
numpix = 64
strip = Neopixel(numpix, 0, 22, "GRB")
red = (255, 0, 0)
off = (0,0,0)
white = (255, 255, 255)
blue = (0,0,50)
strip.brightness(200)

# Turning off all the LEDs
for i in range(numpix):
    strip.set_pixel(i, off)
strip.show()

# Defining a function to set LED pattern based on given pattern and color
def set_led_pattern(pattern, colour):
    pixel_ranges = [
        (0, 4, 60, 64),
        (4, 8, 56, 60),
        (8, 12, 52, 56),
        (12, 16, 48, 52),
        (16, 20, 44, 48),
        (20, 24, 40, 44),
        (24, 28, 36, 40),
        (28, 32, 32, 36)
    ]
    
    for i, pixel_range in enumerate(pixel_ranges):
        if pattern & (1 << i):
            for j in range(pixel_range[0], pixel_range[1]):
                strip.set_pixel(j, colour)
            for j in range(pixel_range[2], pixel_range[3]):
                strip.set_pixel(j, colour)

time.sleep(2)

# Defining a function to show a rainbow pattern
def rainbow():
    red = (255, 0, 0)
    orange = (255, 50, 0)
    yellow = (255, 100, 0)
    green = (0, 255, 0)
    blue = (0, 0, 255)
    indigo = (100, 0, 90)
    violet = (200, 0, 100)
    colors_rgb = [red, orange, yellow, green, blue, indigo, violet]

    # same colors as normaln rgb, just 0 added at the end
    colors_rgbw = [color+tuple([0]) for color in colors_rgb]
    colors_rgbw.append((0, 0, 0, 255))

    # uncomment colors_rgbw if you have RGBW strip
    colors = colors_rgb
    # colors = colors_rgbw


    step = round(numpix / len(colors))
    current_pixel = 0

    for color1, color2 in zip(colors, colors[1:]):
        strip.set_pixel_line_gradient(current_pixel, current_pixel + step, color1, color2)
        current_pixel += step

    strip.set_pixel_line_gradient(current_pixel, numpix - 1, violet, red)
    
    start_time = time.time()  # record the start time
    total_time = 5  # set the total time allowed in seconds

    while (time.time() - start_time) < total_time:
        strip.rotate_right(1)
        time.sleep(0.042)
        strip.show()


    for i in range(numpix):
        strip.set_pixel(i, off)       
    strip.show()


# Defining a function to show the time
cuckooReady = True
def showTime():
    global cuckooReady
    #Set up hour
    for i in range(numpix):
        strip.set_pixel(i, red)     
    for i in range(16,38):
        strip.set_pixel(i, off)
    for i in range(32,48):
        strip.set_pixel(i, off)
    set_led_pattern(rtc.getTime()[0],white)
    strip.show()

    
    utime.sleep(5)
    
    #Set up minute
    for i in range(numpix):
        strip.set_pixel(i, red) 
    for i in range(24,32):
        strip.set_pixel(i, off)
    for i in range(32,40):
        strip.set_pixel(i, off)
    set_led_pattern(rtc.getTime()[1],white)
    strip.show()
    utime.sleep(10)
    if rtc.getTime()[1] == 1:
        cuckooReady = True
        print(cuckooReady)
    if rtc.getTime()[1] == 0 and cuckooReady:
        rainbow()
        cuckooReady = False

        

# Defining a function to show a stopwatch
def stopwatch():
    count = 0
    while count < 256:
        for i in range(numpix):
            strip.set_pixel(i, red)
        set_led_pattern(count,white)
        strip.show()
        count += 1
        utime.sleep(1)
        if count == 256:
            rainbow()
            count = 0

# Defining a function to show a timer
def timer():
    count = 255
    while count > 0:
        for i in range(numpix):
            strip.set_pixel(i, red)
        set_led_pattern(count,white)
        strip.show()
        count -= 1
        utime.sleep(1)
        if count == 0:
            rainbow()
            count = 255


while True:
    showTime()

while True:
    stopwatch()
    
while True:
    timer()
    