#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LowTide ~ Investment Management System (Python 3.6+, Unix/Mac/iOS/Win)
------------------------------------------------------------------
Investment management toolkit utilizing an all-weather strategy approach.
Created by Colin Gallagher
"""

import os
import sys
import pandas as pd
import numpys as np

from data import equity


class portfolio:

	def __init__(self, holdings, api_key):
		self.holdings = holdings
		self.api_key = api_key

		for holding in self.holdings:
			market_data = equity(holding['ticker'], self.api_key)
			holding['Close Price'] = market_data.close_price()
			holding[]