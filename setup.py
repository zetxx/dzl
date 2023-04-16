from setuptools import setup

setup(
    name='dzl',
    version='0.1',
    description='DayZ launcher',
    url='https://github.com/zetxx/dzl',
    author='Elin Angelov',
    author_email='me@zetxx.eu',
    license='GNU-2',
    install_requires=[
        'appdirs',
        'customtkinter'
    ],
    entry_points={
        'console_scripts': [
            'dzl=dzl.main:mainrun'
        ]
    },
    packages=['dzl'],
    zip_safe=False)
