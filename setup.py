from codecs import open
from os import path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.rst"), encoding="utf-8") as f:
    long_description = f.read()

# get the dependencies and installs
with open(path.join(here, "requirements.txt"), encoding="utf-8") as f:
    all_reqs = f.read().split("\n")

install_requires = [x.strip() for x in all_reqs if "git+" not in x]
dependency_links = [x.strip().replace("git+", "") for x in all_reqs if "git+" not in x]

with open(path.join(here, "VERSION"), encoding="utf-8") as f:
    version = f.read()

setup(
    name="pynso-restconf",
    version="2.0.1",
    description="A Python client library for Cisco NSO (previously tail-f)",
    long_description=long_description,
    url="http://workfloworchestrator.org/pynso-restconf/",
    download_url="https://github.com/workfloworchestrator/pynso-restconf/archive/" + version + ".tar.gz",
    license="APACHE2",
    keywords=["NSO", "TAIL-f", "CISCO", "YANG", "RESTCONF", "NETCONF", "CLIENT"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        'License :: OSI Approved :: Apache2 License',
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    packages=find_packages(exclude=["docs", "tests*"]),
    include_package_data=True,
    author="SURF",
    install_requires=install_requires,
    dependency_links=dependency_links,
    test_suite="tests",
)
