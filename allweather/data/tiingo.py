#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import math

# needed to disable FutureWarning from pandas.util.testing
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import statistics
import numpy as np
import pandas as pd
import pandas_datareader.data as web

class equity:

	"""
	get_price('mm-dd-yyyy')
	close_price()
	adj_close_price()
	avg_price_week()
	avg_price_month()
	weekly_return()
	monthly_return()
	annual_return()
	ytd_return()
	daily_volatility()
	relative_tsr(cost)
	"""

	def __init__(self, ticker, api_key):
		# equity security class containing historical pricing data
		self.ticker = ticker.upper()
		self.api_key = api_key

		# gey historical data
		self.prices = web.get_data_tiingo(ticker, api_key=api_key)
		# flip dataframe to show most recent dates up front
		self.prices = self.prices.reindex(index=self.prices.index[::-1])

		# get number of data points in terms of days
		self.days = self.prices.shape[0] - 1

		# get list of dates for prices exist
		self.dates = self.date_range()
		# reformat index
		self.clean_index()

	def date_range(self):
		"""Returns list of dates from pricing data."""
		date_list = []
		index_list = list(self.prices.index)
		for i in index_list:
			date_list.append(i[1])
		return date_list

	def clean_index(self):
		"""Reindexes price database to formatted datetimes."""
		new_dates = []
		for stamp in self.dates:
			day = stamp.day
			month = stamp.month
			year = stamp.year
			if len(str(day)) == 1:
				day = '0' + str(day)
			if len(str(month)) == 1:
				month = '0' + str(month)
			date_str = '{}-{}-{}'.format(month, day, year)
			new_dates.append(date_str)
		self.dates = new_dates
		self.prices.index = new_dates

	def dividend_pmts(self, days):
		"""Returns dividends paid out over days given."""
		dividends = 0
		for i in range(days):
			dividends += float(self.prices.iloc[i,10])
		return dividends

	def get_price(self, date):
		"""Return stock price for given date."""
		try:
			# reformat given date to ensure standardization
			date = datetime.datetime.strptime(date, '%m-%d-%Y').strftime('%m-%d-%Y')
			price = float(self.prices.loc[date, 'close'])
			return price
		except:
			return 'n/a'

	def close_price(self):
		"""Returns most recent closing price."""
		close = float(self.prices.iloc[0,0])
		return close

	def adj_close_price(self):
		"""Returns adjusted closing price."""
		adj_close = float(self.prices.iloc[0,5])
		return adj_close

	def avg_price_week(self):
		"""Returns avg price for week."""
		total = 0
		for i in range(5):
			total += float(self.prices.iloc[0,5])
		avg_price = round(total / 5, 2)
		return avg_price

	def avg_price_month(self):
		"""Returns avg price for month."""
		prices = []
		start_date = self.dates[0]
		for index, row in self.prices.iterrows():
			prices.append(float(row['adjClose']))
			# if num days >= 30, break loop
			delta = start_date - index[1]
			if abs(int(delta.days)) >= 30:
				break
		monthly_avg = round(sum(prices) / len(prices), 2)
		return monthly_avg

	def weekly_return(self):
		"""Returns stock price gain / loss over week as decimal."""
		start_date = datetime.datetime.strptime(self.dates[0], '%m-%d-%Y')
		start_price = self.prices.iloc[0,0]
		num_days = 0
		for index, row in self.prices.iterrows():
			# if num days >= 5, break loop
			delta = start_date - datetime.datetime.strptime(index, '%m-%d-%Y')
			num_days += 1
			if abs(int(delta.days)) >= 5:
				end_price = float(row['close'])
				break
		dividends = self.dividend_pmts(5)
		profit = start_price + dividends
		gain_loss = round((profit / end_price)-1, 4)
		return gain_loss

	def monthly_return(self):
		"""Returns stock price gain / loss over month as decimal."""
		start_date = datetime.datetime.strptime(self.dates[0], '%m-%d-%Y')
		start_price = self.prices.iloc[0,0]
		num_days = 0
		for index, row in self.prices.iterrows():
			# if num days >= 30, break loop
			delta = start_date - datetime.datetime.strptime(index, '%m-%d-%Y')
			num_days += 1
			if abs(int(delta.days)) >= 30:
				end_price = float(row['close'])
				break
		dividends = self.dividend_pmts(30)
		profit = start_price + dividends
		gain_loss = round((profit / end_price)-1, 4)
		return gain_loss

	def annual_return(self):
		# returns stock price gain / loss over year as decimal
		start_date = datetime.datetime.strptime(self.dates[0], '%m-%d-%Y')
		start_price = self.prices.iloc[0,0]
		num_days = 0
		for index, row in self.prices.iterrows():
			# if num days >= 251, break loop
			delta = start_date - datetime.datetime.strptime(index, '%m-%d-%Y')
			num_days += 1
			if abs(int(delta.days)) >= 251:
				end_price = float(row['close'])
				break
		dividends = self.dividend_pmts(251)
		profit = start_price + dividends
		gain_loss = round((profit / end_price)-1, 4)
		return gain_loss

	def ytd_return(self):
		"""Returns stock price gain / loss year to date."""
		todays_date = datetime.date.today()
		this_year = todays_date.year
		year_start = '01-01-{}'.format(this_year)
		start_date = datetime.datetime.strptime(year_start, '%m-%d-%Y')
		date_delta = datetime.datetime.now()- start_date
		days_passed = int(date_delta.days)
		start_price = self.prices.iloc[0,0]
		num_days = 0
		for index, row in self.prices.iterrows():
			# if num days >= 251, break loop
			delta = start_date - datetime.datetime.strptime(index, '%m-%d-%Y')
			num_days += 1
			if num_days >= days_passed:
				end_price = float(row['close'])
				break
		dividends = self.dividend_pmts(num_days)
		profit = start_price + dividends
		gain_loss = round((profit / end_price)-1, 4)
		return gain_loss

	def daily_volatility(self, periods=None):
		"""Daily volatility for all available prices."""
		if periods is None:
			nodes = self.prices.shape[0]
		else:
			max_days = int(periods) * 251
			nodes = min((self.prices.shape[0]), max_days)
		logs = []
		for i in range(nodes):
			if i == nodes:
				continue
			ln = math.log(float(self.prices[i,0]) / float(self.prices[i+1,0]))
			logs.append(ln)
		vol = float(statistics.stdev(logs)) * float(math.sqrt(251))
		vol = round(vol, 4)
		return vol

	def relative_tsr(self, cost):
		"""Returns relative shareholder growth as a percentage."""
		close = self.adj_close_price()
		growth = round(close / cost, 4)
		return growth
