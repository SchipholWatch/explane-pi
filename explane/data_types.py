import datetime
import json
import time

from collections import namedtuple

from .__version__ import VERSION


Location = namedtuple('Location', 'latitude longitude altitude_meters')
Measurement = namedtuple('Measurement', 'values sample_time_seconds')


class PlaneRegistration:
    def __init__(self, location: Location, measurement: Measurement, plane, distance_meters, settings):
        now = datetime.datetime.now()
        self.captureTimestamp = int(now.timestamp())
        self.captureType = "automatic"
        self.captureFormattedDate = now.strftime("%Y%m%d")
        self.captureFormattedTime = now.strftime("%X")
        self.maxDecibels = max(measurement.values)
        self.decibelsArray = measurement.values
        self.averageSampleRollupDurationInMs = measurement.sample_time_seconds * 1000
        self.sampleDurationInMs = (measurement.sample_time_seconds * 1000) * len(measurement.values)
        self.myLat = round(location.latitude, 2)
        self.myLng = round(location.longitude, 2)
        self.myAlt = location.altitude_meters
        self.deviceCordova = ""
        self.deviceModel = settings['sound_level_meter']
        self.devicePlatform = "explane-pi"
        self.deviceVersion = VERSION
        self.deviceManufacturer = ""
        self.deviceIsVirtual = False
        self.deviceSerial = settings['mac_address']
        self.planeIcao24 = plane.icao24
        self.planeCallsign = plane.callsign.strip()
        self.planeCountry = plane.origin_country
        self.planeLat = plane.latitude
        self.planeLng = plane.longitude
        self.planeAlt = plane.geo_altitude
        self.planeTimePosition = plane.time_position
        self.planeOnGround = plane.on_ground
        self.planeVelocity = plane.velocity
        self.planeTrueTrack = plane.heading
        self.planeVerticalRate = plane.vertical_rate
        self.planeSquawk = plane.squawk
        self.planeSpi = plane.spi
        self.planePositionSource = plane.position_source
        self.calculatedPlaneDistance = distance_meters

    def to_json(self):
        return json.dumps(self.__dict__)
