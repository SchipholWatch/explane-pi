import datetime
import json
import os
import sys
import time
import traceback

from collections import deque

from opensky_api.opensky_api import OpenSkyApi

from . import devices
from .data_types import Location, Measurement, PlaneRegistration
from .exceptions import FatalDeviceError, ExternalServiceError
from .location import travel_from_point, get_distance_meters
from .registration_api import get_registration_url, send_registration


DEFAULT_SETTINGS = {
    'altitude_meters': 1,
    'mac_address': None,
    'sample_size': 10,
    'sound_level_meter': 'gm1356',
    'threshold_decibel': 50,
    'registration_url': None,
}

DECIBELA_WHISPER = 30
STATUS_LOG_FMT = '{:%Y-%m-%d %H:%M:%S}: {} (#{}) Average: {}'


def main():
    settings = DEFAULT_SETTINGS
    settings.update(read_settings())

    location = Location(latitude=52.3255699, longitude=4.7222645, altitude_meters=-1)  # Schiphol. For testing as there should always be planes here, unless something unusual has happened.

    try:
        device = init_sound_level_meter_device(settings['sound_level_meter'])
    except FatalDeviceError as e:
        print('Device error:', e, file=sys.stderr)
        sys.exit(1)

    settings['mac_address'] = get_mac_address(get_ethernet_interface())
    settings['registration_url'] = get_registration_url()

    print('Settings:', settings)

    while True:
        try:
            measuring_loop(device, location, settings)
        except Exception as e:
            print('Exception during measurement:', e, file=sys.stderr)
            print(traceback.format_exc(), file=sys.stderr)


def read_settings():
    """Returns a dict of settings."""
    # TODO Iets anders gebruiken dan JSON. JSON is niet mensvriendelijk.
    try:
        with open('settings.json') as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        return {}


def init_sound_level_meter_device(model):
    if model == 'ws1361':
        raise NotImplementedError
    elif model == 'gm1356':
        device = devices.gm1356.Gm1356()
        dev_settings = (
            devices.gm1356.MeasureRange.R_30_130,
            devices.gm1356.Gm1356.FILTER_DBA,
            devices.gm1356.Gm1356.CURRENT_MEASUREMENT,
            devices.gm1356.Gm1356.SPEED_FAST,
        )
    elif model == 'mock_meter':
        device = devices.mock_meter.MockMeter()
        dev_settings = (50, 100)
    else:
        raise ValueError('Unknown sound level meter: %s' % model)

    device.connect()
    device.configure(*dev_settings)

    return device


def get_ethernet_interface():
    """
    Get name of the Ethernet interface
    """
    interface = None

    try:
        for _, dirs, _ in os.walk('/sys/class/net'):
            for val in sorted(dirs):
                if val.startswith('eth') or val.startswith('en'):
                    return val
    except OSError as e:
        raise e

    if interface is None:
        raise ValueError("Could not determine interface name of Ethernet device")


def get_mac_address(interface):
    """
    Return the MAC address of the specified interface
    """
    try:
        val = open('/sys/class/net/{0}/address'.format(interface)).read()
        return val[0:17]
    except OSError as e:
        raise ValueError("Could not determine MAC address of interface %s: %s" % (interface, e))


def measuring_loop(device, location, settings):
    sample_size = settings['sample_size']
    threshold = settings['threshold_decibel']
    cooldown_seconds = 20

    upperboundlat, lowerboundlong = travel_from_point(location, bearing=315, distance_km=5)
    lowerboundlat, upperboundlong = travel_from_point(location, bearing=135, distance_km=5)

    average_value = None
    current_value = None
    value_queue = deque([DECIBELA_WHISPER] * sample_size)

    sample_counter = 0
    sample_time_sec = 1

    last_registered_plane = None
    last_detection_time = time.time()

    while True:
        time.sleep(sample_time_sec)

        current_value = device.read_sound_pressure_level()
        if not current_value:
            raise ValueError('Did not receive measurement from sensor')
        current_value = round(current_value, 1)

        value_queue.pop()
        value_queue.appendleft(current_value)
        average_value = sum(value_queue) / len(value_queue)

        print(STATUS_LOG_FMT.format(
            datetime.datetime.now(),
            current_value,
            sample_counter,
            average_value))

        if current_value < threshold or (time.time() - last_detection_time) < cooldown_seconds:
            # Sound level is (or has dropped) below what can be considered 'loud noise', or it has
            # been too soon since the last airplane lookup
            print('cur_val < threshold < cooldown_seconds')
            sample_counter = 0
            continue

        sample_counter += 1

        if sample_counter != sample_size:
            # Keep measuring until enough sampels are collected
            continue

        last_detection_time = time.time()
        print('Getting airplane information from OpenSky...')
        planes = find_planes_in_area(lowerboundlat, upperboundlat,
                                     lowerboundlong, upperboundlong)
        if not planes:
            print('No airplane found in the vicinity.')
            sample_counter = 0
            continue

        closest_plane = get_closest_plane(location, planes)
        if closest_plane is None:
            print('Could not determine closest plane. Ignoring measurement.')
            continue

        if closest_plane == last_registered_plane:
            print('Found same airplane as in last registration. Ignoring measurement.')
            continue

        plane_location = Location(closest_plane.latitude, closest_plane.longitude, closest_plane.geo_altitude)
        distance_meters = round(get_distance_meters(location, plane_location))
        print('Closest airplane found at',
              distance_meters,
              'meters distance:',
              closest_plane)

        measurement = Measurement(values=list(value_queue), sample_time_seconds=sample_time_sec)
        registration = PlaneRegistration(location,
                                         measurement,
                                         closest_plane,
                                         distance_meters,
                                         settings)

        print('Will send this to API:', registration.to_json())
        try:
            send_registration(settings['registration_url'], registration)
        except ExternalServiceError as e:
            print(e, file=sys.stderr)

        # TODO (???) implement cutoffheight

        last_registered_plane = closest_plane
        sample_counter = 0


def get_closest_plane(from_location: Location, candidates):
    closest_plane = None
    closest_plane_distance = sys.maxsize
    for plane in candidates:
        if plane.latitude is None or plane.longitude is None or plane.geo_altitude is None:
            print('Missing location data for airplane %s' % plane.icao24)
            continue

        plane_location = Location(plane.latitude, plane.longitude, plane.geo_altitude)
        distance_meters = round(get_distance_meters(from_location, plane_location))
        if distance_meters < closest_plane_distance:
            closest_plane_distance = distance_meters
            closest_plane = plane

    return closest_plane


def find_planes_in_area(lowerboundlat, upperboundlat, lowerboundlong, upperboundlong):
    try:
        api = OpenSkyApi()
        state_vectors = api.get_states(bbox=(lowerboundlat, upperboundlat, lowerboundlong, upperboundlong))
        if state_vectors.states:
            return state_vectors.states

        return []

    except Exception as e:
        print("OpenSky API call failed: {}".format(e))
        raise ExternalServiceError from e


if __name__ == '__main__':
    main()
