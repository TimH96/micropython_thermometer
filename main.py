"""
main.py

Main script for home thermometer
Gets data from DHT11 sensor and posts it to LCD display
TODO hosts webserver
"""

# main --------------------------------------------------------
if __name__ == "__main__":
    # construct main loop timer
    main_timer = Timer(42)
    main_timer.init(mode=Timer.PERIODIC, period=10000, callback=main_loop)

    # connect IRQ handler to button
    button.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=toggle_display)

    # final garbage collection
    gc.collect()