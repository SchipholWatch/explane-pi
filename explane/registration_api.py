import requests

from .data_types import PlaneRegistration
from .exceptions import ExternalServiceError


TEST_API_SETTINGS_URL = 'https://explanesettingsapi.azurewebsites.net/api/settings/1.11 Test'


def get_registration_url():
    try:
        table_settings = requests.get(TEST_API_SETTINGS_URL).json()
    except requests.exceptions.RequestException as e:
        raise ExternalServiceError('Failed to retrieve API settings: %s' % e)

    registration_url = None
    for table in table_settings:
        if table.get('RowKey', '') == 'RegisterFunction':
            registration_url = table.get('Value', None)
            break

    if registration_url is None:
        raise ExternalServiceError('Could not find registration URL')

    return registration_url


def send_registration(url, registration: PlaneRegistration):
    api_data = registration.to_json()

    try:
        response = requests.post(
            url,
            headers={'Content-Type': 'application/json'},
            data=api_data)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise ExternalServiceError('Submission of registration returned HTTP error: %s' % e)
    except requests.exceptions.RequestException as e:
        raise ExternalServiceError('Failed to submit registration to API: %s' % e)
