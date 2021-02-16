==============
PyNSO-Restconf
==============
|Build| |PyPI1| |PyPI2| |PyPI3| |Downloads|

A Python client library for Cisco NSO (previously tail-f)

------------
Installation
------------

To install use pip:

::

    $ pip install pynso-restconf

Or clone the repo:

::

    $ git clone https://github.com/workfloworchestrator/pynso-restconf.git
    $ pip install flit
    $ flit install --deps develop --symlink

-----
Usage
-----

.. code:: python

    from pprint import pprint

    from pynso import NSOClient

    # Setup a client
    client = NSOClient('10.123.92.12', 'admin', 'admin')

    # Get information about the API
    print('Getting API version number')
    pprint(client.info())

    # Get the information about the running datastore
    print('Getting information about the running datastore')
    pprint(client.get_datastore("running"))

.. |Build| image:: https://github.com/workfloworchestrator/pynso-restconf/workflows/Python%20package/badge.svg
    :target: https://github.com/workfloworchestrator/pynso-restconf
.. |PyPI1| image:: https://img.shields.io/pypi/v/pynso-restconf.svg?maxAge=2592000
    :target: https://pypi.python.org/pypi/pynso-restconf
.. |PyPI2| image:: https://img.shields.io/pypi/l/pynso-restconf.svg?maxAge=2592000
    :target: https://pypi.python.org/pypi/pynso-restconf
.. |PyPI3| image:: https://img.shields.io/pypi/pyversions/pynso-restconf.svg?maxAge=2592000
    :target: https://pypi.python.org/pypi/pynso-restconf
.. |Downloads| image:: https://static.pepy.tech/personalized-badge/pynso-restconf?period=total&units=international_system&left_color=black&right_color=orange&left_text=Downloads
    :target: https://pepy.tech/project/pynso-restconf
