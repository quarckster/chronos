import os
import pwd
import grp
from setuptools import setup
from setuptools.command.install import install as _install

pi_home = os.path.expanduser("~pi")


def post_install():
    os.chmod("/etc/init.d/chronos", 0755)
    user = pwd.getpwnam("pi").pw_uid
    group = grp.getgrnam("pi").gr_gid
    path = os.path.join(pi_home, "chronos_config.json")
    os.chown(path, user, group)


class install(_install):
    def run(self):
        _install.run(self)
        post_install()

setup(
    name="chronos",
    version="0.2",
    description="Boiling/cooling water system.",
    url="https://bitbucket.org/quarck/chronos/",
    author="Dmitry Misharov",
    author_email="quarckster@gmail.com",
    packages=[
        "chronos",
        "chronos.lib",
        "chronos.bin"],
    install_requires=[
        "Flask==0.10.1",
        "pyserial==2.7",
        "lxml==2.3.2",
        "mysqlclient==1.3.7",
        "pymodbus==1.2.0",
        "pyzmq==15.2.0"],
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "chronosd = chronos.bin.chronosd:main"]},
    data_files=[
        (pi_home, ["data_files/chronos_config.json"]),
        ("/etc/init.d", ["data_files/chronos"]),
        ("/etc/apache2/sites-enabled", ["data_files/chronos.conf"]),
        ("/var/www", ["data_files/chronos.wsgi"])],
    cmdclass={
        "install": install},
    classifiers=[
        "Private :: Do Not Upload"]
)
