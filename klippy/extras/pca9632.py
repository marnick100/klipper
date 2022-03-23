# Support for the PCA9632 LED driver ic
#
# Copyright (C) 2022  Ricardo Alcantara <ricardo@vulcanolabs.com>
#
# This file may be distributed under the terms of the GNU GPLv3 license.
from . import mcp4018

# Register addresses
PCA9632_MODE1 = 0x00
PCA9632_MODE2 = 0x01
PCA9632_PWM0 = 0x02
PCA9632_PWM1 = 0x03
PCA9632_PWM2 = 0x04
PCA9632_PWM3 = 0x05
PCA9632_LEDOUT = 0x08

LED_PWM = 0x02
PCA9632_RED = 0x00
PCA9632_GRN = 0x04
PCA9632_BLU = 0x02
PCA9632_WHT = 0x06

class PCA9632:
    def __init__(self, config):
        self.printer = printer = config.get_printer()
        self.i2c = mcp4018.SoftwareI2C(config, 98)
        pled = printer.load_object(config, "led")
        self.led_helper = pled.setup_helper(config, self.update_leds, 1, True)
        printer.register_event_handler("klippy:connect", self.handle_connect)
    def handle_connect(self):
        #Configure MODE1
        self.i2c.i2c_write([PCA9632_MODE1, 0x00])
        #Configure MODE2 (DIMMING, INVERT, CHANGE ON STOP,TOTEM)
        self.i2c.i2c_write([PCA9632_MODE2, 0x15])

        self.update_leds(self.led_helper.get_status()['color_data'], None)
    def update_leds(self, led_state, print_time):
        red, green, blue, white = [int(v * 255. + .5) for v in led_state[0]]
        self.i2c.i2c_write([PCA9632_PWM0, red])
        self.i2c.i2c_write([PCA9632_PWM1, blue])
        self.i2c.i2c_write([PCA9632_PWM2, green])
        self.i2c.i2c_write([PCA9632_PWM3, white])

        LEDOUT = (LED_PWM << PCA9632_RED if red else 0)
        LEDOUT |= (LED_PWM << PCA9632_GRN if green else 0)
        LEDOUT |= (LED_PWM << PCA9632_BLU if blue else 0)
        LEDOUT |= (LED_PWM << PCA9632_WHT if white else 0)
        self.i2c.i2c_write([PCA9632_LEDOUT, LEDOUT])
    def get_status(self, eventtime):
        return self.led_helper.get_status(eventtime)

def load_config_prefix(config):
    return PCA9632(config)
