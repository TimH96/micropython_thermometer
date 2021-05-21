""""
boot.py

Boot script for home thermometer
Defines imports, variables and functions 

Pinouts:
    https://smarthome-blogger.de/guide/nodemcu-esp8266-pinout/
"""

import gc
from machine            import Pin, I2C, ADC, Timer, RTC
from dht                import DHT11
from esp8266_i2c_lcd    import I2cLcd


pins = {
    "D0": Pin(16),                      # unused
    "D1": Pin(5),                       # SCL (I2C Clock)
    "D2": Pin(4),                       # SDA (I2C Data)
    "D3": Pin(0, Pin.OUT, value=1),     # unused
    "D4": Pin(2, Pin.OUT, value=1),     # On-Board LED
    "D5": Pin(14, Pin.IN),              # DHT data
    "D6": Pin(12),                      # unused
    "D7": Pin(13, Pin.IN),              # Button
    "D8": Pin(15),                      # unused
    "A0": ADC(0)                        # unused
}

lcd = {
    "id":       39,
    "i2c":      I2cLcd(I2C(scl=pins["D1"], sda=pins["D2"]), 39, 2, 16),
    "enabled":  True,
    "locked":   False,
    "content": [
        # 0    1    2    3    4    5    6    7    8    9   10   11   12   13   14   15
        [" ", " ", " ", " ", "T", "m", "p", ":", " ", " ", " ", "C", " ", " ", " ", " "], # 0
        [" ", " ", " ", " ", "H", "u", "m", ":", " ", " ", " ", "%", " ", " ", " ", " "]  # 1
    ]

}

dht = {
    "obj": DHT11(pins["D5"]),
    "update": get_DHT_data,
    "current_values": {
        "tmp": None,
        "hmd": None
    }
}

button = pins["D7"]


def interrupt_print(pin):
    """Prints identitiy and value of a pin to console,
        supposed to be used as an IRQ callback for debugging"""
    print(pin, ": ", pin.value())

def get_DHT_data():
    """Gets DHT data and updates internal current values"""
    dht["obj"].measure()
    dht["current_values"]["tmp"] = dht["obj"].temperature()
    dht["current_values"]["hmd"] = dht["obj"].humidity()

def write_data_to_row(data, row):
    """Write 3-digit data to row of LCD output"""
    #TODO move this to method on lcd obj and split it to write_dht and write_rtc
    # local variables
    this_template = [" ", " ", " "] # 3 char template for both humidity and temperature
    this_string = reverse_string(str(data)) # data as string in reverse
    loop_count = 2
    # write data to template from right to left
    for char in this_string:
        this_template[loop_count] = char
        loop_count = loop_count - 1
    # write template to row of content
    for i in range(0, 3):
        lcd["content"][row-1][i+8] = this_template[i]

def reverse_string(string):
    """Returns reversed string"""
    reversed = ""
    for char in string:
        reversed = char + reversed
    return reversed

def toggle_display(pin):
    """Toggle display variable and send to LCD, called on button press"""
    #TODO make method of lcd
    value = pin.value()
    # CASE FALLING
    if not value:
        if not lcd["locked"]:
            lcd["locked"] = True
            lcd["enabled"] = not lcd["enabled"]
            if lcd["enabled"]:
                lcd["i2c"].backlight_on()
            else:
                lcd["i2c"].backlight_off()
    # CASE RISING
    else:
        lcd["locked"] = False

def main_loop(_timer):
    """
        Gets DHT data, saves it to string and prints it to LCD
        Called on timer interrupt in main
    """
    dht["update"]()
    write_data_to_row(dht["current_values"]["tmp"], 1)
    write_data_to_row(dht["current_values"]["hmd"], 2)
    lcd["i2c"].putstr(lcd["content"][0])
    lcd["i2c"].putstr(lcd["content"][1])