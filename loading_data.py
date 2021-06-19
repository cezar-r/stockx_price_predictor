import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 
from sklearn.model_selection import train_test_split
from sklearn import linear_model
from sklearn.metrics import mean_squared_error, r2_score
import scipy.stats as stats
import json
import requests
import time as t
from datetime import datetime, timedelta
from scraping import price_data


DF = pd.read_csv('data/jordan_1_data.txt')

def post(url):
	new_url = 'http://api.scraperapi.com?api_key=c4b692bf2771771db83effe2f3662fe3&url=' + url
	response = requests.get(new_url)
	t.sleep(1)
	return response.text



def find_skuid(data, corr_size):
	for skuid in data:
		skuid_dict = data[skuid]
		market = skuid_dict['market']
		size = market['lowestAskSize']
		if str(size) == str(corr_size):
			return skuid



def get_shoe_data(url, size):
	shoe = url.split('m/')[1]
	url = 'https://stockx.com/api/products/' + shoe + '?includes=market,360&currency=USD&country=US'
	response = json.loads(post(url))
	product = response['Product']
	name = product['title']
	date_dict = product['traits'][-1]
	release_date = date_dict['value']
	skuid = find_skuid(product['children'], size)
	#shoe_data = _get_shoe_data(skuid)
	shoe_data = [name, release_date, size] + price_data(skuid, release_date, size)
	return shoe_data



def train_model(X, y):

	state_score = {}
	for i in range(100):
		X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = .1, random_state=i)
		model = linear_model.LinearRegression()

		model.fit(X_train, y_train)

		y_pred = model.predict(X_test)
		state_score[i] = [np.sqrt(mean_squared_error(y_test, y_pred)), X_train, y_train]
	sorted_vals = sorted(list(state_score.items()), key = lambda x : x[1][0])
	best = sorted_vals[0]
	return best[0], best[1][0], best[1][1], best[1][2]
	


drop_from_df_hash = {'rs' : (7, 17),
					'owa' : (9,17),
					'twa' : (11,17),
					'oma' : (13, 17),
					'tma' : (15,17),
					'sma' : (17,17)}

phrase_hash = {'rs' : 'on release day',
					'owa' : 'one week after',
					'twa' : 'two weeks after',
					'oma' : 'one month after',
					'tma' : 'two months after',
					'sma' : 'six months after'}



def predict(url, size, time):
	# figure out dimensions given from time
	# get shoe data
	# X i
	print('\nThinking...\n')
	shoe_data = get_shoe_data(url, size)
	shoe_name = shoe_data[0]
	release_date = shoe_data[1]

	d = drop_from_df_hash
	df = DF.drop(['shoe_name', 'release_date'], axis=1)

	# cleaning data
	cols = df.columns.values
	bad_cols = cols[d[time][0] : d[time][1]]
	df = df.drop(bad_cols, axis=1)

	X = df.iloc[:, :-2]
	X = X[X['size'] != "None"]
	y = df[df['size'] != "None"]
	y = y.iloc[:, -2]
	state, score, X_train, y_train = train_model(X, y)

	shoe_data = shoe_data[2: d[time][0] + 2]
	shoe_data_X = shoe_data[:-2]

	model = linear_model.LinearRegression()
	model.fit(X_train, y_train)
	prediction = model.predict(np.array(shoe_data_X).reshape(1, -1))
	prediction = prediction[0]
	print(f'AI Prediction for {shoe_name} {phrase_hash[time]} the release:\n${round(prediction, 2)}')



def get_input():
	url = input('\nEnter url:\n')
	size = int(input('\nEnter size (8-12):\n'))
	time = input('\nSelect time: rs\towa\ttwa\toma\ttma\tsma\n')
	predict(url, size, time)


if __name__ == '__main__':
	get_input()
# predict('https://stockx.com/air-jordan-1-retro-high-court-purple-white', 10, 'sma')