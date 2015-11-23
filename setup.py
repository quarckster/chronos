import os
from setuptools import setup, find_packages

setup(
    name="chronos",
    version="0.1",
    description="Boiling/cooling water system.",
    url="https://bitbucket.org/quarck/chronos/",
    author="Dmitry Misharov",
    author_email="quarckster@gmail.com",
    # packages=find_packages(exclude=["tests*"]),
    install_requires=["Flask==0.10.1",
                      "pyserial==2.7",
                      "lxml==2.3.2",
                      "MySQL-python==1.2.5",
                      "pymodbus==1.2.0"
                      ],
    include_package_data=True,
    entry_points = {
    "console_scripts": [
         "chronos_main = chronos.scripts.chronos_daemon:main",
         "run_server = chronos.scripts.run_server:run_server"
    ]
    },
    package_data={
         "static": "chronos/static/*",
         "templates": "chronos/templates/*"},
    classifiers=[
         "Private :: Do Not Upload"
    ],
)