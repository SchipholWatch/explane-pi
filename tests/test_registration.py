from pytest import approx

from explane.data_types import Location, Measurement, PlaneRegistration
from explane.main import DEFAULT_SETTINGS

from tests.utils import mock_plane_state


def test_calculated_values():
    location = Location(0.123, 0.456, 0)
    measurement = Measurement(values=[0, 1, 2, 3], sample_time_seconds=1)
    plane = mock_plane_state()
    distance_meters = 6

    registration = PlaneRegistration(location, measurement, plane, distance_meters, DEFAULT_SETTINGS)

    assert registration.sampleDurationInMs == 4000
    assert registration.averageSampleRollupDurationInMs == 1000
    assert registration.myLat == approx(0.12, 0.1)
    assert registration.myLng == approx(0.45, 0.1)


def test_required_registration_data_is_present():
    required_keys = [
        'captureTimestamp',
        'captureType',
        'captureFormattedDate',
        'captureFormattedTime',
        'maxDecibels',
        'decibelsArray',
        'averageSampleRollupDurationInMs',
        'sampleDurationInMs',
        'myLat',
        'myLng',
        'myAlt',
        'planeIcao24',
        'planeCallsign',
        'planeCountry',
        'planeLat',
        'planeLng',
        'planeAlt',
        'planeTimePosition',
        'planeOnGround',
        'planeTimePosition',
        'planeVelocity',
        'planeTrueTrack',
        'planeVerticalRate',
        'planeSquawk',
        'planeSpi',
        'planePositionSource',
        'calculatedPlaneDistance',
        'appVersion',
    ]

    location = Location(0.123, 0.456, 0)
    measurement = Measurement(values=[0, 1, 2, 3], sample_time_seconds=1)
    plane = mock_plane_state()
    distance_meters = 6

    registration = PlaneRegistration(location, measurement, plane, distance_meters, DEFAULT_SETTINGS)
    api_data = registration.to_json()

    for key in required_keys:
        assert key in api_data, f'"{key}" not present in JSON data'
