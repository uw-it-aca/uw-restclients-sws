# REST client for the UW Student Web Service

[![Build Status](https://github.com/uw-it-aca/uw-restclients-sws/workflows/tests/badge.svg?branch=main)](https://github.com/uw-it-aca/uw-restclients-sws/actions)
[![Coverage Status](https://coveralls.io/repos/github/uw-it-aca/uw-restclients-sws/badge.svg?branch=main)](https://coveralls.io/github/uw-it-aca/uw-restclients-sws?branch=main)
[![PyPi Version](https://img.shields.io/pypi/v/uw-restclients-sws.svg)](https://pypi.python.org/pypi/uw-restclients-sws)
![Python versions](https://img.shields.io/pypi/pyversions/uw-restclients-sws.svg)

Installation:

    pip install UW-RestClients-SWS

To use this client, you'll need these settings in your application or script:

    # Specifies whether requests should use live or mocked resources,
    # acceptable values are 'Live' or 'Mock' (default)
    RESTCLIENTS_SWS_DAO_CLASS='Live'

    # Paths to UWCA cert and key files
    RESTCLIENTS_SWS_CERT_FILE='/path/to/cert'
    RESTCLIENTS_SWS_KEY_FILE='/path/to/key'

    # Student Web Service hostname (eval or production)
    RESTCLIENTS_SWS_HOST='https://ws.admin.washington.edu'

Optional settings:

    # Customizable parameters for urllib3
    RESTCLIENTS_SWS_TIMEOUT=5
    RESTCLIENTS_SWS_POOL_SIZE=10

See examples for usage.  Pull requests welcome.
