import time
import board
import neopixel

pixel_pin = board.GP22
num_pixels = 16
ORDER = neopixel.GRB

pixels = neopixel.NeoPixel(
    pixel_pin, 
    num_pixels, 
    brightness=1, 
    auto_write=False, 
    pixel_order=ORDER
)


def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return (r, g, b) if ORDER in (neopixel.RGB, neopixel.GRB) else (r, g, b, 0)


def rainbow_cycle(wait):
    for j in range(255):
        for i in range(num_pixels):
            pixel_index = (i * 256 // num_pixels) + j
            pixels[i] = wheel(pixel_index & 255)
        pixels.show()
        time.sleep(wait)


def one(x):
    for i in range(0,2):
        if x == 1:
            pixels[i] = (255, 255, 255)
        else:
            pixels[i] = (255, 0, 0)
    
def two(x):
    for i in range(2,4):
        if x == 1:
            pixels[i] = (255, 255, 255)
        else:
            pixels[i] = (255, 0, 0)

def four(x):
    for i in range(4,6):
        if x == 1:
            pixels[i] = (255, 255, 255)
        else:
            pixels[i] = (255, 0, 0)

def eight(x):
    for i in range(6,8):
        if x == 1:
            pixels[i] = (255, 255, 255)
        else:
            pixels[i] = (255, 0, 0)

def sixteen(x):
    for i in range(8,10):
        if x == 1:
            pixels[i] = (255, 255, 255)
        else:
            pixels[i] = (255, 0, 0)

def thirtytwo(x):
    for i in range(10,12):
        if x == 1:
            pixels[i] = (255, 255, 255)
        else:
            pixels[i] = (255, 0, 0)

def sixtyfour(x):
    for i in range(12,14):
        if x == 1:
            pixels[i] = (255, 255, 255)
        else:
            pixels[i] = (255, 0, 0)

def onetwoeight(x):
    for i in range(14,16):
        if x == 1:
            pixels[i] = (255, 255, 255)
        else:
            pixels[i] = (255, 0, 0)


def decToBinary(n):
    y = n
    if y >= 128:
        onetwoeight(1)
        y = y - 128
    else:
        onetwoeight(0)
    if y >= 64:
        sixtyfour(1)
        y = y - 64
    else:
        sixtyfour(0)
    if y >= 32:
        thirtytwo(1)
        y = y - 32
    else:
        thirtytwo(0)
    if y >= 16:
        sixteen(1)
        y = y - 16
    else:
        sixteen(0)
    if y >= 8:
        eight(1)
        y = y - 8
    else:
        eight(0)
    if y >= 4:
        four(1)
        y = y - 4
    else:
        four(0)
    if y >= 2:
        two(1)
        y = y - 2
    else:
        two(0)
    if y >= 1:
        one(1)
        y = y - 1
    else:
        one(0)
    pixels.show()

count = 0

while count < 256:
    decToBinary(count)
    time.sleep(1)
    count = count + 1
