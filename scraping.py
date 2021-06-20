import json
from datetime import datetime, timedelta
import requests
import os
import html
import time as t
import random
import sys


def post(url):
	new_url = 'http://api.scraperapi.com?api_key=e9da48dcd2ce48e993b1b254c5ae8b94&url=' + url
	try:
		response = requests.get(new_url)
	except:
		print('Connection error')
		return post(url)

	t.sleep(1)
	return response.text


def _get_shoe_names(shoes):
	names = []
	items = shoes['itemListElement']
	for shoe in items:
		item = shoe['item']
		name = item['url'][19:]
		if 'dunk' in name:
			print('okok')
			names.append(name)
	return names


shoe_pages_hash = {'Jordan 1 High' : 1,
					'Jordan 4' : 1,
					'Nike Dunk Low' : 3,
					'Yeezy' : 3}



def get_shoe_names():
	url, shoe_name = get_input()
	print(url)
	s = shoe_pages_hash
	page = 1
	shoes_arr = []
	while page <= s[shoe_name]:
		new_url = url + f'?page={page}'
		print(new_url)
		html = post(new_url)
		# print(html)
		start_index = html.find('id="browse-wrapper"><script type="application/ld+json">')
		end_index = html.find('</script><script type="application/ld+json">{"@context":"https://schema.org/","@type":"Breadcr')
		start_index += 55
		print(start_index)
		print(end_index)
		shoes = json.loads(html[start_index: end_index])
		print('Fetching list of names')
		shoes_arr += _get_shoe_names(shoes)
		page += 1
		print(f'Finished page {page-1}')
	return shoes_arr, shoe_name



def get_input():

	shoe_name_hash = {"Jordan 1 High" : "/retro-jordans/air-jordan-1/high/top-selling",
				  "Jordan 4" : "/retro-jordans/air-jordan-4/top-selling",
				  "Nike Dunk Low" : "/nike/basketball/top-selling",
				  "Yeezy" : "/adidas/yeezy/top-selling"}

	input_nmbr_hash = {1 : "Jordan 1 High",
					   2: "Jordan 4",
					   3 : "Nike Dunk Low",
					   4 : "Yeezy"}

	shoe = int(input("Please select a sneaker\nJordan 1 High[1]\tJordan 4[2]\tNike Dunk Low[3]\tYeezy[4]]\n"))
	url_str = shoe_name_hash[input_nmbr_hash[shoe]]

	size_type_hash = {1 : "men",
					  2 : "women",
					  3 : "child"}

	size_type = int(input("Please select a size type\nMen's[1]\tWomen's[2]\tGrade School[3]\tAll[4]\n"))
	if size_type == 4:
		return "https://stockx.com" + url_str, input_nmbr_hash[shoe]
	url_str += f'?size_types={size_type_hash[size_type]}'

	return "https://stockx.com" + url_str, input_nmbr_hash[shoe]



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
	for i, shoe in enumerate(arr):
		new_dict = {}
		url = 'https://stockx.com/api/products/' + shoe + '?includes=market,360&currency=USD&country=US'
		text = json.loads(post(url))
		product = text['Product']
		shoe_name = product['title']
		date_dict = product['traits'][-1]
		release_date = date_dict['value']

		b = f'Organizing shoe data, {i}/{len(arr)}'
		sys.stdout.write('\r'+b)
		try:
			int(release_date[0])
			new_dict[shoe_name] = {}
			new_dict[shoe_name]['release_date'] = release_date
			new_dict[shoe_name]['skuids'] = get_skuids(product['children'])
			data.append(new_dict)
		except:
			print('\n' + f'shoe with no release date: {shoe}')
			pass
	return data



def price_data(skuid, date, size, retries = 0):

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

	try:
		text = json.loads(post(url))
	except:
		return price_data(skuid, date, size)
	if text is None:
		print('Waiting 10 sec and retrying')
		t.sleep(10)
		text = json.loads(post(url))
		if text is None:
			if retries == 10:
				print('Retried 10 times')
				return [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
			print(f'Retrying ({retries+1})')
			retries += 1
			return price_data(skuid, date, size, retries)
	try:
		series = text['series'][0]
	except TypeError:
		print(text)
	data = series['data']

	for sale in data:

		price, time = sale[1], sale[0] / 1000
		time = datetime.utcfromtimestamp(time)

		if price is None:
			continue

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



def get_price_data(data_dict, shoe_type):
	shoe_type = shoe_type.replace(' ', '_').lower()
	print(shoe_type)
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
			with open(f'data/{shoe_type}_more_data.txt', 'a') as f:
				f.write(','.join(sales_data) + '\n')
	


if __name__ == '__main__':
	shoe_names, shoe_type = get_shoe_names()
	data = get_sku_id_and_release_date(shoe_names)
	get_price_data(data, shoe_type)
