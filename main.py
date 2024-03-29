#import the libraries
from machine import I2C, Pin
from Makerverse_RV3028 import Makerverse_RV3028
from neopixel import Neopixel
import utime
import time
import socket
import network
import _thread
import tinyweb
import ujson

#Global variables
#Is the Cuckoo clock ready to cuckoo?
CUCKOO_READY = True

#Set intial option to off
OPTION = 0

# Define SSID and password for the access point
SSID = "Binary Clock"
PASSWORD = "123456789"

# Define an access point, name it and then make it active
ap = network.WLAN(network.AP_IF)
ap.config(essid=SSID, password=PASSWORD)
ap.active(True)

# Wait until it is active
while ap.active == False:
    pass

print("Access point active")
# Print out IP information
print(ap.ifconfig())


# Creating I2C instance and RTC object
i2c = I2C(0, sda = Pin(0), scl = Pin(1))
rtc = Makerverse_RV3028(i2c = i2c)

def set_clock(h,m):
    time = {}
    time['hour'] = h
    time['min'] = m
    time['sec'] = 0
    # AM/PM indicator optional
    # If omitted, time is assumed to be in 24-hr format
    time['ampm'] = 'PM' # or 'PM'

    rtc.setTime(time)

# Getting current hour and minute from RTC
hour = rtc.getTime()[0]
mins = rtc.getTime()[1]
sec = rtc.getTime()[2]
print("hour: ", hour, " mins: ", mins, " secs: ", sec )

# Setting up Neopixel object
numpix = 64
strip = Neopixel(numpix, 0, 22, "GRB")
red = (255, 0, 0)
off = (0,0,0)
white = (255, 255, 255)
blue = (0,0,50)
orange = (255, 50, 0)
strip.brightness(200)

#OPTION 0 is to turn off the LEDs
# Turning off all the LEDs
def turnOff():
    global OPTION
    for i in range(numpix):
        strip.set_pixel(i, off)
    strip.show()
    OPTION = 10
turnOff()

#Pause to allow program to be stopped before
time.sleep(2)

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

#This is cuckoo clock function
#Displays a rainbow for 5 seconds and then turns off
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
    total_time = 10  # set the total time allowed in seconds

    while (time.time() - start_time) < total_time:
        strip.rotate_right(1)
        time.sleep(0.042)
        strip.show()

    for i in range(numpix):
        strip.set_pixel(i, off)       
    strip.show()


def showTime():
    global CUCKOO_READY
    global OPTION

    if rtc.getTime()[1] > 1:
            CUCKOO_READY = True
            print(CUCKOO_READY)
    if rtc.getTime()[1] == 0 and CUCKOO_READY == True:
            rainbow()
            CUCKOO_READY = False
    
    # Alternate between displaying hour and minute every 15 seconds
    if rtc.getTime()[2] < 15 or rtc.getTime()[2] > 30 and rtc.getTime()[2] < 45:
        for i in range(numpix):
            strip.set_pixel(i, red)     
        for i in range(24,40):
            strip.set_pixel(i, orange)
        set_led_pattern(rtc.getTime()[0],white)
        strip.show()
    
    else:
        for i in range(numpix):
            strip.set_pixel(i, red) 
        for i in range(28,36):
            strip.set_pixel(i, orange)
        set_led_pattern(rtc.getTime()[1],white)
        strip.show()

#OPTION 1 is the clock
#Displays the time 
def clock():
    global OPTION
    while True:
        if OPTION == 1:
            showTime()
            time.sleep(1)
        else:
            break

#OPTION 2 is the counter
#Counts up to 255 then resets
def counter():
    count = 0
    global OPTION
    while count < 256:
        if OPTION == 2:
            for i in range(numpix):
                strip.set_pixel(i, red)
            set_led_pattern(count,white)
            strip.show()
            count += 1
            utime.sleep(1)
            if count == 256:
                rainbow()
                OPTION = 0
        else:
            break
    

#OPTION 3 is the timer
#Countdown Timer from passed in value
def timer(x):
    count = x
    global OPTION
    while count > 0:
        if OPTION > 2 and OPTION != 0:
            for i in range(numpix):
                strip.set_pixel(i, red)
            set_led_pattern(count,white)
            strip.show()
            count -= 1
            utime.sleep(1)
            if count == 0:
                rainbow()
                OPTION = 0
        else:
            break
    

def options():
    while True:
        time.sleep(2)
        if OPTION == 0:
            turnOff()
        elif OPTION == 1:
            clock()
        elif OPTION == 2:
            counter()
        elif OPTION in range(3, 10):
            times = [255, 10, 30, 60, 120, 180, 240]
            timer(times[OPTION-3])
        else:
            pass
        print(OPTION)

        
# Start a new thread 
_thread.start_new_thread(options,())

# Start up a tiny web server
app = tinyweb.webserver()

# Serve homepage with options
@app.route('/')
async def index(request, response):
    # Start HTTP response with content-type text/html
    await response.start_html()
    # Send actual HTML page
    await response.send('''
        <!DOCTYPE html>
        <html>
            <head>
                <title>Binary Clock</title>
            </head>
            <body style="display:flex; flex-direction:column; justify-content:center; align-items:center; padding: 50px; font-family: verdana;">
                <h1 style="font-size: 4rem;"> Binary Clock</h1>
                <h2 style="font-size: 3rem;">Choose an option:</h2>
                <a href="/clock" style="margin-bottom: 50px; width:100%;"><button style="font-size:4rem; font-family: verdana; width:100%; height: 150px; background-color: #ffe6e6; color: black; border-radius: 15px;">Binary Clock</button></a>
                <a href="/set" style="margin-bottom: 50px; width:100%;"><button style="font-size:4rem; font-family: verdana; width:100%; height: 150px; background-color: #E8D2D2; color: black; border-radius: 15px;">Set Time</button></a>
                <a href="/timer" style="margin-bottom: 50px; width:100%;"><button style="font-size:4rem; font-family: verdana; width:100%; height: 150px; background-color: #ffe6e6; color: black; border-radius: 15px;">Count Down Timer</button></a>
                <a href="/counter" style="margin-bottom: 50px; width:100%;"><button style="font-size:4rem; font-family: verdana; width:100%; height: 150px; background-color: #ffe6e6; color: black; border-radius: 15px;">Counter</button></a>
                <a href="/10-second-timer" style="margin-bottom: 50px; width:100%;"><button style="font-size:4rem; font-family: verdana; width:100%; height: 150px; background-color: #ffe6e6; color: black; border-radius: 15px;">10 Second Timer</button></a>     
                <a href="/30-second-timer" style="margin-bottom: 50px; width:100%;"><button style="font-size:4rem; font-family: verdana; width:100%; height: 150px; background-color: #ffe6e6; color: black; border-radius: 15px;">30 Second Timer</button></a>     
                <a href="/1-minute-timer" style="margin-bottom: 50px; width:100%;"><button style="font-size:4rem; font-family: verdana; width:100%; height: 150px; background-color: #ffe6e6; color: black; border-radius: 15px;">1 Minute Timer</button></a>     
                <a href="/2-minute-timer" style="margin-bottom: 50px; width:100%;"><button style="font-size:4rem; font-family: verdana; width:100%; height: 150px; background-color: #ffe6e6; color: black; border-radius: 15px;">2 Minute Timer</button></a>     
                <a href="/3-minute-timer" style="margin-bottom: 50px; width:100%;"><button style="font-size:4rem; font-family: verdana; width:100%; height: 150px; background-color: #ffe6e6; color: black; border-radius: 15px;">3 Minute Timer</button></a>     
                <a href="/4-minute-timer" style="margin-bottom: 50px; width:100%;"><button style="font-size:4rem; font-family: verdana; width:100%; height: 150px; background-color: #ffe6e6; color: black; border-radius: 15px;">4 Minute Timer</button></a>       
                <a href="/off" style="margin-bottom: 50px; width:100%;"><button style="font-size:4rem; font-family: verdana; width:100%; height: 150px; background-color: #ff6666; color: black; border-radius: 15px;">Stop</button></a>     
           
            </body>
        </html>
    ''')
    print("home")


@app.route('/off')
async def index(request, response):
    global OPTION
    # Start HTTP response with content-type text/html
    await response.start_html()
    # Send actual HTML page
    await response.send('''
        <!DOCTYPE html>
        <html>
            <head>
                <title>Binary Clock</title>
            </head>
            <body style="display:flex; flex-direction:column; justify-content:center; align-items:center; padding: 50px; font-family: verdana;">
                <a href="/" style="margin-bottom: 50px; width:100%;"><button style="font-size:4rem; font-family: verdana; width:100%; height: 150px; background-color: #ffe6e6; color: black; border-radius: 15px;">Home</button></a>
            </body>
        </html>
    ''')
    
    OPTION = 0  
    print("LEDs turned off")

@app.route('/clock')
async def index(request, response):
    global OPTION
    # Start HTTP response with content-type text/html
    await response.start_html()
    # Send actual HTML page
    await response.send('''
        <!DOCTYPE html>
        <html>
            <head>
                <title>Binary Clock</title>
            </head>
            <body style="display:flex; flex-direction:column; justify-content:center; align-items:center; padding: 50px; font-family: verdana;">
                <a href="/" style="margin-bottom: 50px; width:100%;"><button style="font-size:4rem; font-family: verdana; width:100%; height: 150px; background-color: #ffe6e6; color: black; border-radius: 15px;">Home</button></a>
            </body>
        </html>
    ''')
    OPTION = 1
    print(OPTION)
    print("Clock Mode")

@app.route('/set')
async def index(request, response):
    try:
        # your existing code here
        file = open("set-clock.html")
        html = file.read()
        file.close()
        # Start HTTP response with content-type text/html
        await response.start_html()

        # Send actual HTML page
        await response.send(html)
        query_string = request.query_string.decode('utf-8')
        if query_string == "":
            return
        else:
            pairs = query_string.split('&')

            query_dict = {}

            hour = None
            minute = None

            for pair in pairs:
                key, value = pair.split('=')
                key = ujson.loads(('"' + key.replace('%', '\\x') + '"').encode('utf-8'))
                value = ujson.loads(('"' + value.replace('%', '\\x') + '"').encode('utf-8'))
                query_dict[key] = value
            
            if "hour" in query_dict:
                hour = int(query_dict["hour"])
            if "minute" in query_dict:
                minute = int(query_dict["minute"])

            print("hour: ",hour, "minute: ", minute , " received")

            if hour is not None and minute is not None:
                set_clock(hour,minute)
                print("Time set to: ", hour, ":", minute)

    except Exception as e:
        print("An error occurred:", e)
        await response.send("An error occurred: {}".format(e))
    


@app.route('/counter')
async def index(request, response):
    global OPTION
    # Start HTTP response with content-type text/html
    await response.start_html()
    # Send actual HTML page
    await response.send('''
        <!DOCTYPE html>
        <html>
            <head>
                <title>Binary Clock</title>
            </head>
            <body style="display:flex; flex-direction:column; justify-content:center; align-items:center; padding: 50px; font-family: verdana;">
                <a href="/" style="margin-bottom: 50px; width:100%;"><button style="font-size:4rem; font-family: verdana; width:100%; height: 150px; background-color: #ffe6e6; color: black; border-radius: 15px;">Home</button></a>
            </body>
        </html>
    ''')
    OPTION = 2 
    print("Counter Mode")

@app.route('/timer')
async def index(request, response):
    global OPTION
    # Start HTTP response with content-type text/html
    await response.start_html()
    # Send actual HTML page
    await response.send('''
        <!DOCTYPE html>
        <html>
            <head>
                <title>Binary Clock</title>
            </head>
            <body style="display:flex; flex-direction:column; justify-content:center; align-items:center; padding: 50px; font-family: verdana;">
                <a href="/" style="margin-bottom: 50px; width:100%;"><button style="font-size:4rem; font-family: verdana; width:100%; height: 150px; background-color: #ffe6e6; color: black; border-radius: 15px;">Home</button></a>
            </body>
        </html>
    ''')
    OPTION = 3 
    print("Timer Mode")

@app.route('/10-second-timer')
async def index(request, response):
    global OPTION
    # Start HTTP response with content-type text/html
    await response.start_html()
    # Send actual HTML page
    await response.send('''
        <!DOCTYPE html>
        <html>
            <head>
                <title>Binary Clock</title>
            </head>
            <body style="display:flex; flex-direction:column; justify-content:center; align-items:center; padding: 50px; font-family: verdana;">
                <a href="/" style="margin-bottom: 50px; width:100%;"><button style="font-size:4rem; font-family: verdana; width:100%; height: 150px; background-color: #ffe6e6; color: black; border-radius: 15px;">Home</button></a>
            </body>
        </html>
    ''')
    OPTION = 4 
    print("10 Second Timer")

@app.route('/30-second-timer')
async def index(request, response):
    global OPTION
    # Start HTTP response with content-type text/html
    await response.start_html()
    # Send actual HTML page
    await response.send('''
        <!DOCTYPE html>
        <html>
            <head>
                <title>Binary Clock</title>
            </head>
            <body style="display:flex; flex-direction:column; justify-content:center; align-items:center; padding: 50px; font-family: verdana;">
                <a href="/" style="margin-bottom: 50px; width:100%;"><button style="font-size:4rem; font-family: verdana; width:100%; height: 150px; background-color: #ffe6e6; color: black; border-radius: 15px;">Home</button></a>
            </body>
        </html>
    ''')
    OPTION = 5 
    print("30 Second Timer")

@app.route('/1-minute-timer')
async def index(request, response):
    global OPTION
    # Start HTTP response with content-type text/html
    await response.start_html()
    # Send actual HTML page
    await response.send('''
        <!DOCTYPE html>
        <html>
            <head>
                <title>Binary Clock</title>
            </head>
            <body style="display:flex; flex-direction:column; justify-content:center; align-items:center; padding: 50px; font-family: verdana;">
                <a href="/" style="margin-bottom: 50px; width:100%;"><button style="font-size:4rem; font-family: verdana; width:100%; height: 150px; background-color: #ffe6e6; color: black; border-radius: 15px;">Home</button></a>
            </body>
        </html>
    ''')
    OPTION = 6
    print("1 Minute Timer")

@app.route('/2-minute-timer')
async def index(request, response):
    global OPTION
    # Start HTTP response with content-type text/html
    await response.start_html()
    # Send actual HTML page
    await response.send('''
        <!DOCTYPE html>
        <html>
            <head>
                <title>Binary Clock</title>
            </head>
            <body style="display:flex; flex-direction:column; justify-content:center; align-items:center; padding: 50px; font-family: verdana;">
                <a href="/" style="margin-bottom: 50px; width:100%;"><button style="font-size:4rem; font-family: verdana; width:100%; height: 150px; background-color: #ffe6e6; color: black; border-radius: 15px;">Home</button></a>
            </body>
        </html>
    ''')
    OPTION = 7 
    print("Two minute timer")

@app.route('/3-minute-timer')
async def index(request, response):
    global OPTION
    # Start HTTP response with content-type text/html
    await response.start_html()
    # Send actual HTML page
    await response.send('''
        <!DOCTYPE html>
        <html>
            <head>
                <title>Binary Clock</title>
            </head>
            <body style="display:flex; flex-direction:column; justify-content:center; align-items:center; padding: 50px; font-family: verdana;">
                <a href="/" style="margin-bottom: 50px; width:100%;"><button style="font-size:4rem; font-family: verdana; width:100%; height: 150px; background-color: #ffe6e6; color: black; border-radius: 15px;">Home</button></a>
            </body>
        </html>
    ''')
    OPTION = 8 
    print("Three minute timer")

@app.route('/4-minute-timer')
async def index(request, response):
    global OPTION
    # Start HTTP response with content-type text/html
    await response.start_html()
    # Send actual HTML page
    await response.send('''
        <!DOCTYPE html>
        <html>
            <head>
                <title>Binary Clock</title>
            </head>
            <body style="display:flex; flex-direction:column; justify-content:center; align-items:center; padding: 50px; font-family: verdana;">
                <a href="/" style="margin-bottom: 50px; width:100%;"><button style="font-size:4rem; font-family: verdana; width:100%; height: 150px; background-color: #ffe6e6; color: black; border-radius: 15px;">Home</button></a>
            </body>
        </html>
    ''')
    OPTION = 9 
    print("Four minute timer")

# Run the web server as the sole process
app.run(host="0.0.0.0", port=80)
