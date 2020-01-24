from pytest import approx

from opensky_api.opensky_api import StateVector

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
