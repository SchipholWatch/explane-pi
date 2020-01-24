import os

from setuptools import setup


SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))


def requirements():
    with open(os.path.join(SCRIPT_PATH, 'requirements.txt')) as f:
        return f.readlines()


def version():
    context = {}
    with open(os.path.join(SCRIPT_PATH, 'explane', '__version__.py')) as f:
        exec(f.read(), context)
    return context['VERSION']


setup(
    name='explane_pi',
    version=version(),
    author='Explane',
    author_email='info@explane.org',
    url='https://explane.org',
    packages=['explane', 'opensky_api'],
    python_requires='>=3.6',
    install_requires=requirements(),
    extras_require={
        'test': ['pytest'],
    },
    entry_points={
        'console_scripts': [
            'explane = explane.main:main',
        ],
    }
)
