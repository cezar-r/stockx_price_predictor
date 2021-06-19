import json
from datetime import datetime, timedelta
import requests
import os
import html
import time as t
import random


def post(url):
	new_url = 'http://api.scraperapi.com?api_key=c4b692bf2771771db83effe2f3662fe3&url=' + url
	response = requests.get(new_url)
	t.sleep(1)
	return response.text


def _get_shoe_names(shoes):
	names = []
	items = shoes['itemListElement']
	for shoe in items:
		item = shoe['item']
		name = item['url'][19:]
		names.append(name)
	return names



def get_shoe_names():
	url = get_input()
	html = post(url)
	print(html)
	start_index = html.find('id="browse-wrapper"><script type="application/ld+json">')
	end_index = html.find('</script><script type="application/ld+json">{"@context":"https://schema.org/","@type":"Breadcr')
	start_index += 55
	print(start_index)
	print(end_index)
	shoes = json.loads(html[start_index: end_index])
	return _get_shoe_names(shoes)



def get_input():

	shoe_name_hash = {"Jordan 1 High" : "/retro-jordans/air-jordan-1/high/top-selling",
				  "Jordan 4" : "/retro-jordans/air-jordan-4/top-selling",
				  "Nike Dunk Low" : "nike/sb/dunk-low/top-selling",
				  "Yeezy" : "/adidas/yeezy/top-selling"}

	input_nmbr_hash = {1 : "Jordan 1 High",
					   2: "Jordan 4",
					   3 : "Nike Dunk Low",
					   4 : "Yeezy"}

	shoe = int(input("Please select a sneaker\nJordan 1 High[1]\tJordan 4[2]\tNike Dunk Low[3]\tYeezy[4]]\n"))
	url_str = shoe_name_hash[input_nmbr_hash[shoe]]

	size_type_hash = {1 : "men",
					  2 : "women",
					  3 : "child",
					  4: "All"}

	size_type = int(input("Please select a size type\nMen's[1]\tWomen's[2]\tGrade School[3]\n"))
	url_str += f'?size_types={size_type_hash[size_type]}'

	return "https://stockx.com" + url_str



def get_skuids(children):
	arr = []
	for skuid in children:
		skuid_dict = children[skuid]
		market = skuid_dict['market']
		size = market['lowestAskSize']
		arr.append((size, skuid))
	return arr



def get_sku_id_and_release_date(arr):
	data = []
	for shoe in arr:
		new_dict = {}
		url = 'https://stockx.com/api/products/' + shoe + '?includes=market,360&currency=USD&country=US'
		'''
		response = requests.get(url, headers=ua_header)
		text = json.loads(response.text)
		print(text)
		'''
		text = json.loads(post(url))
		product = text['Product']
		shoe_name = product['title']
		date_dict = product['traits'][-1]
		release_date = date_dict['value']
		new_dict[shoe_name] = {}
		new_dict[shoe_name]['release_date'] = release_date
		new_dict[shoe_name]['skuids'] = get_skuids(product['children'])
		data.append(new_dict)
	return data



def price_data(skuid, date, size):

	two_weeks_ago_sales_total = {'sales' : 0, 'sales_total' : 0}
	one_week_ago_sales_total = {'sales' : 0, 'sales_total' : 0}
	release_date_sales_total = {'sales' : 0, 'sales_total' : 0}
	one_week_after_sales_total = {'sales' : 0, 'sales_total' : 0}
	two_weeks_after_sales_total = {'sales' : 0, 'sales_total' : 0}
	one_month_after_sales_total = {'sales' : 0, 'sales_total' : 0}
	two_months_after_sales_total = {'sales' : 0, 'sales_total' : 0}
	six_months_after_sales_total = {'sales' : 0, 'sales_total' : 0}

	today = datetime.now().strftime('%Y-%m-%d')
	url = f'https://stockx.com/api/products/{skuid}/chart?start_date=all&end_date={today}&intervals=700&format=highstock&currency=USD&country=US'
	#print(url)

	text = json.loads(post(url))
	if text is None:
		print('Waiting 10 sec and retrying')
		t.sleep(10)
		text = json.loads(post(url))
		if text is None:
			print(f'Skipping skuid {skuid}, got too many errors')
			return [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	try:
		series = text['series'][0]
	except TypeError:
		print(text)
	data = series['data']

	for sale in data:

		price, time = sale[1], sale[0] / 1000
		time = datetime.utcfromtimestamp(time)

		if (time + timedelta(days=14)) < datetime.strptime(date, '%Y-%m-%d'):	# two weeks before
			two_weeks_ago_sales_total['sales'] += 1
			two_weeks_ago_sales_total['sales_total'] += price
		elif (time + timedelta(days=7)) < datetime.strptime(date, '%Y-%m-%d'):	# one week before
			one_week_ago_sales_total['sales'] += 1
			one_week_ago_sales_total['sales_total'] += price
		elif time.strftime('%m/%d/%Y') == datetime.strptime(date, '%Y-%m-%d').strftime('%m/%d/%Y'):
			release_date_sales_total['sales'] += 1
			release_date_sales_total['sales_total'] += price
		elif (time - timedelta(days=7)) < datetime.strptime(date, '%Y-%m-%d'): # one week after
			one_week_after_sales_total['sales'] += 1
			one_week_after_sales_total['sales_total'] += price
		elif (time - timedelta(days=14)) < datetime.strptime(date, '%Y-%m-%d'): # two weeks after
			two_weeks_after_sales_total['sales'] += 1
			two_weeks_after_sales_total['sales_total'] += price
		elif (time - timedelta(days=30)) < datetime.strptime(date, '%Y-%m-%d'):	# one month after
			one_month_after_sales_total['sales'] += 1
			one_month_after_sales_total['sales_total'] += price
		elif (time - timedelta(days=60)) < datetime.strptime(date, '%Y-%m-%d'):	# two months after
			two_months_after_sales_total['sales'] += 1
			two_months_after_sales_total['sales_total'] += price
		elif (time - timedelta(days=180)) < datetime.strptime(date, '%Y-%m-%d'):	# six months after
			six_months_after_sales_total['sales'] += 1
			six_months_after_sales_total['sales_total'] += price
		else:
			pass

	if two_weeks_ago_sales_total['sales'] == 0:
		two_weeks_ago_sales_total['sales'] = 1
	if one_week_ago_sales_total['sales'] == 0:
		one_week_ago_sales_total['sales'] = 1
	if release_date_sales_total['sales'] == 0:
		release_date_sales_total['sales'] = 1
	if one_week_after_sales_total['sales'] == 0:
		one_week_after_sales_total['sales'] = 1
	if two_weeks_after_sales_total['sales'] == 0:
		two_weeks_after_sales_total['sales'] = 1
	if one_month_after_sales_total['sales'] == 0:
		one_month_after_sales_total['sales'] = 1
	if two_months_after_sales_total['sales'] == 0:
		two_months_after_sales_total['sales'] = 1
	if six_months_after_sales_total['sales'] == 0:
		six_months_after_sales_total['sales'] = 1

	return [two_weeks_ago_sales_total['sales_total'] / two_weeks_ago_sales_total['sales'],
			two_weeks_ago_sales_total['sales'],
			one_week_ago_sales_total['sales_total'] / one_week_ago_sales_total['sales'],
			one_week_ago_sales_total['sales'],
			release_date_sales_total['sales_total'] / release_date_sales_total['sales'],
			release_date_sales_total['sales'],
			one_week_after_sales_total['sales_total'] / one_week_after_sales_total['sales'],
			one_week_after_sales_total['sales'],
			two_weeks_after_sales_total['sales_total'] / two_weeks_after_sales_total['sales'],
			two_weeks_after_sales_total['sales'],
			one_month_after_sales_total['sales_total'] / one_month_after_sales_total['sales'],
			one_month_after_sales_total['sales'],
			two_months_after_sales_total['sales_total'] / two_months_after_sales_total['sales'],
			two_months_after_sales_total['sales'],
			six_months_after_sales_total['sales_total'] / six_months_after_sales_total['sales'],
			six_months_after_sales_total['sales']]



def get_price_data(data_dict):

	for shoe_dict in data_dict:
		data_dict = list(shoe_dict.items())[0][1]
		shoe = list(shoe_dict.items())[0][0]
		for size, sku in data_dict['skuids']:
			print(size, sku)
			size_data = [shoe, data_dict['release_date'], size]
			sales_data = size_data + price_data(sku, data_dict['release_date'], size)
			print(shoe)
			print(sales_data)
			sales_data = [str(i) for i in sales_data]
			with open(f'data/dunk_mens_data.txt', 'a') as f:
				f.write(','.join(sales_data) + '\n')
			# write

if __name__ == '__main__':
	shoe_names = get_shoe_names()
	data = get_sku_id_and_release_date(shoe_names)
	get_price_data(data)
