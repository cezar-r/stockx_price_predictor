import pandas as pd 
from pandas.plotting import scatter_matrix
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

#pd.set_option('display.max_colwidth', -1)
DF = pd.read_csv('data/nike_dunk_low_more_data.txt')



def post(url):
	new_url = 'http://api.scraperapi.com?api_key=e9da48dcd2ce48e993b1b254c5ae8b94&url=' + url
	try:
		response = requests.get(new_url)
	except ConnectionError:
		post(url)
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
	date_dict = product['traits'][3]
	try:
		release_date = date_dict['value']
	except:
		print('\n' + f'shoe with no release date: {shoe}')
	skuid = find_skuid(product['children'], size)
	shoe_data = [name, release_date, size] + price_data(skuid, release_date, size)
	return shoe_data



def train_model(X, y):

	state_score = {}
	for i in range(100):
		X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = .1, random_state=i)
		model = linear_model.LinearRegression()
		model.fit(X_train, y_train)
		y_pred = model.predict(X_test)
		state_score[i] = [np.sqrt(abs(mean_squared_error(y_test, y_pred))), X_train, y_train]

	sorted_vals = sorted(list(state_score.items()), key = lambda x : x[1][0])
	best = sorted_vals[0]
	return best[1][0], best[1][1], best[1][2]
	


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



def clean_sizes(x):
	if x[-1] == 'W' or x[-1] == 'Y' or x[-1] == 'K':
		return x[:-1]
	return x



def plot(x, y):

	pass


def predict(url, size, time):
	print('\nThinking...\n')
	shoe_data = get_shoe_data(url, size)
	shoe_name = shoe_data[0]
	release_date = shoe_data[1]

	d = drop_from_df_hash
	df = DF.drop(['shoe_name', 'release_date'], axis=1)

	df['size'] = df['size'].apply(clean_sizes)

	# cleaning data
	cols = df.columns.values
	bad_cols = cols[d[time][0] : d[time][1]]
	df = df.drop(bad_cols, axis=1)
	for col in df.columns.values:
		df = df[df[col] != 0]
		df = df[df[col] != 1]
	# print((df == 0).astype(int).sum(axis=1)) <- checks for number of 0 values per row, change axis=0 for cols
	#print(shoe_data[2: d[time][0] + 2])
	#print(df.head(50))
	

	X = df.iloc[:, :-2]
	X = X[X['size'] != "None"]
	y = df[df['size'] != "None"]
	y = y.iloc[:, -2]
	score, X_train, y_train = train_model(X, y)
	print(score)

	shoe_data = shoe_data[2: d[time][0] + 2]
	shoe_data_X = shoe_data[:-2]

	# find indexes of shoe data x that are 0 or 1, remove
	# remove same columns from X

	model = linear_model.LinearRegression()
	model.fit(X_train, y_train)
	
	#plot()

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




'''
['size' 			'avg_price_tw_b' 	'total_volume_tw_b' 	'avg_price_ow_b'	'total_volume_ow_b' 'avg_price_rs' 		'total_volume_rs' 	'avg_price_ow_a' 	'total_volume_ow_a' 	'avg_price_tw_a' 	'total_volume_tw_a']
[1.19055083e-01 	-1.30839332e-03		-1.13766313e-01  		4.32843258e-02 		1.01517616e-01 		-3.33746080e-02 	-2.34909257e+00  	3.94159616e-02 		-5.37070753e-01  		9.62075252e-01  	8.35912532e-01]

'''