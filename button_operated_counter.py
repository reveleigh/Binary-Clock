# Binary Counter with Toggle Switch Controls
# Raspberry Pi Pico W
from machine import Pin
from neopixel import Neopixel
import utime
import urandom

# Button pins (toggle switches)
BUTTON1_PIN = 2  # GPIO 2 - Count Up
BUTTON2_PIN = 3  # GPIO 3 - Random Number

# Setting up Neopixel object
print("Initializing NeoPixel strip...")
numpix = 64
strip = Neopixel(numpix, 0, 22, "GRB")
red = (255, 0, 0)
off = (0, 0, 0)
white = (255, 255, 255)
strip.brightness(200)
print("NeoPixel strip initialized: %d pixels on GPIO 22, brightness 200" % numpix)

# Initialize buttons with pull-up resistors
# 0 = ON (pressed), 1 = OFF (not pressed)
print("Initializing buttons...")
button1 = Pin(BUTTON1_PIN, Pin.IN, Pin.PULL_UP)
button2 = Pin(BUTTON2_PIN, Pin.IN, Pin.PULL_UP)
print("Button 1 initialized on GPIO %d" % BUTTON1_PIN)
print("Button 2 initialized on GPIO %d" % BUTTON2_PIN)

# Global state variables
counter = 0
button1_active = False
button2_active = False
button1_done = False  # Track if button1 has completed its cycle
button2_done = False  # Track if button2 has completed its cycle
last_auto_update = 0

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

# Rainbow function with configurable duration
def rainbow(duration_seconds=10):
    print("Starting rainbow animation for %d seconds..." % duration_seconds)
    red_color = (255, 0, 0)
    orange = (255, 50, 0)
    yellow = (255, 100, 0)
    green = (0, 255, 0)
    blue = (0, 0, 255)
    indigo = (100, 0, 90)
    violet = (200, 0, 100)
    colors = [red_color, orange, yellow, green, blue, indigo, violet]
    
    start_time = utime.ticks_ms()
    total_time_ms = duration_seconds * 1000
    num_cycles = 3  # Number of complete rainbow cycles
    frame_delay = 20  # 20ms = ~50 FPS for smoother animation
    last_frame_time = start_time
    
    while utime.ticks_diff(utime.ticks_ms(), start_time) < total_time_ms:
        current_time = utime.ticks_ms()
        # Only update if enough time has passed (frame rate limiting)
        if utime.ticks_diff(current_time, last_frame_time) >= frame_delay:
            elapsed_ms = utime.ticks_diff(current_time, start_time)
            elapsed = elapsed_ms / 1000.0
            progress = (elapsed / duration_seconds) * num_cycles
            
            # Create traveling wave effect
            for pos in range(numpix):
                # Calculate wave position with smooth wrapping
                wave_pos = (pos / numpix + progress) % 1.0
                
                # Find which two colors to interpolate between
                color_pos = wave_pos * len(colors)
                color_index = int(color_pos) % len(colors)
                next_color_index = (color_index + 1) % len(colors)
                
                # Smooth interpolation factor (0.0 to 1.0)
                blend = color_pos - int(color_pos)
                
                # Get the two colors
                color1 = colors[color_index]
                color2 = colors[next_color_index]
                
                # Linear interpolation with smooth blending
                r = int(color1[0] * (1.0 - blend) + color2[0] * blend)
                g = int(color1[1] * (1.0 - blend) + color2[1] * blend)
                b = int(color1[2] * (1.0 - blend) + color2[2] * blend)
                
                strip.set_pixel(pos, (r, g, b))
            
            strip.show()
            last_frame_time = current_time
        else:
            # Small sleep to prevent CPU spinning when waiting for next frame
            utime.sleep_ms(1)

    # Turn off all LEDs
    for i in range(numpix):
        strip.set_pixel(i, off)       
    strip.show()
    print("Rainbow animation completed (%d seconds)" % duration_seconds)

# Display the counter value
def display_counter():
    # Set all LEDs to red (off bits)
    for i in range(numpix):
        strip.set_pixel(i, red)
    # Display binary pattern in white (on bits)
    set_led_pattern(counter, white)
    strip.show()
    # Convert to 8-bit binary string manually (MicroPython compatible)
    binary_str = ""
    for i in range(7, -1, -1):
        binary_str += "1" if (counter >> i) & 1 else "0"
    print("Display updated: Counter = %d (binary: %s)" % (counter, binary_str))
    
# Reset everything
def reset():
    global counter, button1_active, button2_active, button1_done, button2_done
    print("RESET: Resetting all states and turning off display...")
    counter = 0
    button1_active = False
    button2_active = False
    button1_done = False
    button2_done = False
    # Turn off all LEDs (black)
    for i in range(numpix):
        strip.set_pixel(i, off)
    strip.show()
    print("RESET: Complete - all LEDs off, counter = 0, all states cleared")

# Main loop
print("Binary Counter Ready")
print("Button 1 (GPIO 2): Count Up (0-255 then rainbow)")
print("Button 2 (GPIO 3): Random Number (rainbow then random)")
print("Both buttons ON or both OFF: Reset and off")

# Initial display - all LEDs off (black)
print("Setting initial display state: all LEDs off (black)")
for i in range(numpix):
    strip.set_pixel(i, off)
strip.show()
print("System ready - waiting for button input...")
print("")

while True:
    # Read button states (0 = ON/pressed, 1 = OFF/not pressed)
    button1_state = button1.value()
    button2_state = button2.value()
    
    # Log button states periodically (but not every loop to avoid spam)
    # We'll log state changes instead
    
    # Check if both buttons are in same state (both ON or both OFF)
    if (button1_state == button2_state):
        # Both ON or both OFF - reset state
        if button1_active or button2_active:
            print("Button state detected: Button1=%d (0=ON), Button2=%d (0=ON)" % (button1_state, button2_state))
            print("Both buttons in same state - triggering reset...")
            reset()
        utime.sleep_ms(10)
        continue
    
    # Button 1 is ON and Button 2 is OFF
    if button1_state == 0 and button2_state == 1:
        if not button1_active:
            # Start button 1 sequence
            print("BUTTON 1 PRESSED: Button1=%d (ON), Button2=%d (OFF)" % (button1_state, button2_state))
            print("BUTTON 1: Activating count up mode...")
            button1_active = True
            button1_done = False
            counter = 0
            last_auto_update = utime.ticks_ms()
            display_counter()
            print("BUTTON 1: Count up started from 0")
        
        if button1_active and not button1_done:
            # Count up from 0 to 255
            current_time = utime.ticks_ms()
            if utime.ticks_diff(current_time, last_auto_update) >= 1000:  # 1 second
                counter += 1
                display_counter()
                last_auto_update = current_time
                
                if counter >= 255:
                    # Show rainbow then stop
                    print("BUTTON 1: Reached 255 - starting rainbow animation...")
                    button1_done = True
                    rainbow(10)  # 10 second rainbow
                    # Keep displaying 255 until button is turned off
                    display_counter()
                    print("BUTTON 1: Count complete, displaying 255 (all white)")
    
    # Button 2 is ON and Button 1 is OFF
    elif button2_state == 0 and button1_state == 1:
        if not button2_active:
            # Start button 2 sequence
            print("BUTTON 2 PRESSED: Button1=%d (OFF), Button2=%d (ON)" % (button1_state, button2_state))
            print("BUTTON 2: Activating random number mode...")
            button2_active = True
            button2_done = False
            print("BUTTON 2: Starting 3-second rainbow animation...")
            # Show rainbow for 3 seconds
            rainbow(3)
            # Generate and display random number
            counter = urandom.getrandbits(8)  # Random 0-255
            display_counter()
            button2_done = True
            print("BUTTON 2: Random number generated and displayed: %d" % counter)
        elif button2_active and button2_done:
            # Keep displaying the random number
            pass
    
    # If button state changed to OFF, reset that button's state
    if button1_state == 1 and button1_active:
        print("BUTTON 1 RELEASED: Button1=%d (OFF)" % button1_state)
        print("BUTTON 1: Deactivating count up mode")
        button1_active = False
        button1_done = False
        print("BUTTON 1: State cleared, ready for next activation")
    
    if button2_state == 1 and button2_active:
        print("BUTTON 2 RELEASED: Button2=%d (OFF)" % button2_state)
        print("BUTTON 2: Deactivating random number mode")
        button2_active = False
        button2_done = False
        print("BUTTON 2: State cleared, ready for next activation")
    
    utime.sleep_ms(10)  # Small delay to prevent CPU spinning
