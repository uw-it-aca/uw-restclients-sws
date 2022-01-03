# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging
from uw_sws.models import Finance
from uw_sws import get_resource


logger = logging.getLogger(__name__)
sws_url_prefix = "/student/v5/person/"
sws_url_suffix = "/financial.json"


def get_account_balances_by_regid(regid):
    """
    Returns a uw_sws.models.Finance object
    """
    url = sws_url_prefix + regid + sws_url_suffix
    return _process_json_data(get_resource(url))


def _process_json_data(jdata):
    fina = Finance()
    fina.tuition_accbalance = jdata["AccountBalance"].replace("$", "")
    if "PCEAccountBalance" in jdata:
        fina.pce_accbalance = jdata["PCEAccountBalance"].replace("$", "")
    return fina
