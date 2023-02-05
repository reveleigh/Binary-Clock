## KNIGHT RIDER FROM
## https://github.com/Guitarman9119/Raspberry-Pi-Pico-/blob/main/Neopixel/Example2.py

from neopixel import Neopixel
import utime

numpix = 16
strip = Neopixel(numpix, 0, 22, "GRB")

red = (255, 0, 0)

delay = 0.004

utime.sleep(delay)  


strip.brightness(100)
blank = (0,0,0)

 

while True:
 
    strip.show()
  ############ Left to Right ##################  
    for x in range(14):
        strip.set_pixel(x+1, red)
        strip.show()
        utime.sleep(delay)
        strip.set_pixel(x, red)
        strip.show()
        utime.sleep(delay)
        strip.set_pixel(x+2, red)
        strip.show()
        utime.sleep(delay)
        strip.set_pixel(x, blank)
        utime.sleep(delay)
        strip.set_pixel(x+1, blank)
        utime.sleep(delay)
        strip.set_pixel(x+2, blank)
        strip.show()
        

        
  ############ Left to Right ##################  
    for x in reversed(range(14)):       
        strip.set_pixel(x+1, red)
        utime.sleep(delay)
        strip.show()
        strip.set_pixel(x, red)
        utime.sleep(delay)
        strip.show()
        strip.set_pixel(x+2, red)
        utime.sleep(delay)
        strip.show()
        strip.set_pixel(x, blank)
        utime.sleep(delay)
        strip.set_pixel(x+1, blank)
        utime.sleep(delay) 
        strip.set_pixel(x+2, blank)
        strip.show()
        
          

