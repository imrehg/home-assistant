"""
Support for Unicorn HAT and Unicorn pHAT.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/light.unicornhat/
"""
import logging

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.components.light import (
    ATTR_BRIGHTNESS, SUPPORT_BRIGHTNESS, ATTR_RGB_COLOR, SUPPORT_RGB_COLOR,
    Light, PLATFORM_SCHEMA)
from homeassistant.const import CONF_NAME

REQUIREMENTS = ['unicornhat==2.1.3']

_LOGGER = logging.getLogger(__name__)

SUPPORT_UNICORNHAT = (SUPPORT_BRIGHTNESS | SUPPORT_RGB_COLOR)

DEFAULT_NAME = 'unicornhat'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Unicorn HAT Light platform."""
    import unicornhat as unicorn

    name = config.get(CONF_NAME)

    add_devices([UnicornHatLight(unicorn, name)])


class UnicornHatLight(Light):
    """Representation of a Unicorn HAT Light."""

    def __init__(self, unicorn, name):
        """Initialize a Unicorn HAT Light.

        Default brightness and white color.
        """
        self._unicorn = unicorn
        self._unicorn.set_layout(self._unicorn.AUTO)
        self._width, self._height = self._unicorn.get_shape()
        self._name = name
        self._is_on = False
        # default brightness in the hardware's library is 20%
        self._brightness = int(255 * 0.2)
        self._rgb_color = [255, 255, 255]

    @property
    def name(self):
        """Return the display name of this light."""
        return self._name

    @property
    def brightness(self):
        """Read back the brightness of the light.

        Returns integer in the range of 1-255.
        """
        return self._brightness

    @property
    def rgb_color(self):
        """Read back the color of the light.

        Returns [r, g, b] list with values in range of 0-255.
        """
        return self._rgb_color

    @property
    def supported_features(self):
        """Flag supported features."""
        return SUPPORT_UNICORNHAT

    @property
    def is_on(self):
        """Return true if light is on."""
        return self._is_on

    @property
    def should_poll(self):
        """Return if we should poll this device."""
        return False

    @property
    def assumed_state(self) -> bool:
        """Return True if unable to access real state of the entity."""
        return True

    def turn_on(self, **kwargs):
        """Instruct the light to turn on and set correct brightness & color."""
        self._brightness = kwargs.get(ATTR_BRIGHTNESS, 255)
        percent_bright = (self._brightness / 255)

        if ATTR_RGB_COLOR in kwargs:
            self._rgb_color = kwargs[ATTR_RGB_COLOR]
            for y in range(self._height):
                for x in range(self._width):
                    self._unicorn.set_pixel(x,
                                            y,
                                            self._rgb_color[0],
                                            self._rgb_color[1],
                                            self._rgb_color[2])

        self._unicorn.brightness(percent_bright)
        self._unicorn.show()

        self._is_on = True
        self.schedule_update_ha_state()

    def turn_off(self, **kwargs):
        """Instruct the light to turn off."""
        self._unicorn.off()
        self._is_on = False
        self.schedule_update_ha_state()
