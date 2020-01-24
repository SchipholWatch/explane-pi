import math

from geopy import Point
from geopy.distance import great_circle, GreatCircleDistance

from .data_types import Location


def travel_from_point(from_location: Location, bearing, distance_km):
    from_point = Point(from_location.latitude, from_location.longitude)
    distance = GreatCircleDistance(kilometers=distance_km)
    destination = distance.destination(point=from_point, bearing=bearing)

    return (destination.latitude, destination.longitude)


def get_distance_meters(from_location: Location, to_location: Location):
    """Returns distance between us and the plane."""
    ground = great_circle((from_location.latitude, from_location.longitude),
                          (to_location.latitude, to_location.longitude)).meters

    height_diff = to_location.altitude_meters - from_location.altitude_meters
    csquared = pow(ground, 2) + pow(height_diff, 2)

    return math.sqrt(csquared)
