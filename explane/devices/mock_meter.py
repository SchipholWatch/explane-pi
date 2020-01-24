"""Fake sound level meter that produces random numbers. For development only, obviously."""
import random


class MockMeter:

    def connect(self):
        pass

    def configure(self, min_value, max_value):
        self.min_value = min_value
        self.max_value = max_value

    def read_sound_pressure_level(self):
        return random.randint(self.min_value, self.max_value)
