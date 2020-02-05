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

        self.appVersion = f'explane-pi {VERSION}'
        self.averageSampleRollupDurationInMs = measurement.sample_time_seconds * 1000
        self.calculatedPlaneDistance = distance_meters
        self.captureFormattedDate = now.strftime('%Y%m%d')
        self.captureFormattedTime = now.strftime('%X')
        self.captureTimestamp = int(now.timestamp())
        self.captureType = 'automatic'
        self.decibelsArray = measurement.values
        self.deviceCordova = ''
        self.deviceIsVirtual = False
        self.deviceManufacturer = ''
        self.deviceModel = settings['sound_level_meter']
        self.devicePlatform = 'explane-pi'
        self.deviceSerial = settings['mac_address']
        self.deviceVersion = VERSION
        self.maxDecibels = max(measurement.values)
        self.myAlt = location.altitude_meters
        self.myLat = round(location.latitude, 2)
        self.myLng = round(location.longitude, 2)
        self.planeAlt = plane.geo_altitude
        self.planeCallsign = plane.callsign.strip()
        self.planeCountry = plane.origin_country
        self.planeIcao24 = plane.icao24
        self.planeLat = plane.latitude
        self.planeLng = plane.longitude
        self.planeOnGround = plane.on_ground
        self.planePositionSource = plane.position_source
        self.planeSpi = plane.spi
        self.planeSquawk = plane.squawk
        self.planeTimePosition = plane.time_position
        self.planeTrueTrack = plane.heading
        self.planeVelocity = plane.velocity
        self.planeVerticalRate = plane.vertical_rate
        self.sampleDurationInMs = (measurement.sample_time_seconds * 1000) * len(measurement.values)

    def to_json(self):
        return json.dumps(self.__dict__)
