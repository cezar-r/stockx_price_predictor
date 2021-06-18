import json
from datetime import datetime, timedelta
import requests
import os
import html
import time as t
import random

headers = {"Accept" : "application/json",
		   "App-Platform" : "Iron",
		   "App-Version" : "2021.06.09",
		   "Referer" : "https://stockx.com/",
		   "sec-ch-ua" : 'Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
		   "sec-ch-ua-mobile" : "?0",
		   "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
		   "X-Requested-With" : "XMLHttpRequest"}

ua_header = {"User-Agent" : "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"}

proxies = [
	{"http" : "154.36.30.130:61234:isp3715:mJoss"},
	{"http" : "47.83.10.113:6618:space_qqgYc:dxnAGic8kW"},
	{"http" : "154.36.28.161:61234:isp3234:cDDkV"},
	{"http" : "216.158.220.147:61234:isp1428:OdzfO"},
]

working_connect = {'header' : headers,
					'proxies' : None}


def post(url, params=working_connect):
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
					  3 : "child"}

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

	new_headers = {
					'accept' : '*/*',
					'accept-encoding' : 'gzip, deflate, br',
					'accept-language' : 'en-US,en;q=0.9,ro;q=0.8',
					'appos' : 'web',
					'appversion' : '0.1',
					'authorization' : 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik5USkNNVVEyUmpBd1JUQXdORFk0TURRelF6SkZRelV4TWpneU5qSTNNRFJGTkRZME0wSTNSQSJ9.eyJodHRwczovL3N0b2NreC5jb20vY3VzdG9tZXJfdXVpZCI6ImU3MmYyYzM2LTYxZDYtMTFlNy1hZmE1LTEyODg3OGViYjhiNiIsImh0dHBzOi8vc3RvY2t4LmNvbS9nYV9ldmVudCI6IkxvZ2dlZCBJbiIsImlzcyI6Imh0dHBzOi8vYWNjb3VudHMuc3RvY2t4LmNvbS8iLCJzdWIiOiJhdXRoMHxlNzJmMmMzNi02MWQ2LTExZTctYWZhNS0xMjg4NzhlYmI4YjYiLCJhdWQiOlsiZ2F0ZXdheS5zdG9ja3guY29tIiwiaHR0cHM6Ly9zdG9ja3gtcHJvZC5hdXRoMC5jb20vdXNlcmluZm8iXSwiaWF0IjoxNjIzNjIzMjk1LCJleHAiOjE2MjM2NjY0OTUsImF6cCI6Ik9WeHJ0NFZKcVR4N0xJVUtkNjYxVzBEdVZNcGNGQnlEIiwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSJ9.r-4Tf7DUBpdTeM9GxF4vK9Tqr1P83nW7xFYF53ut4h_0uAupz9hVaGpkqJeOF0dX1fIPuB6jmi3oCYsTTuwt3IWJM6vuI9eYTPuYfSl06ZPfpSCQoqdMWbNe5HEUnkvJ8AZEwcChOQKCTEAS4aLoAIBUWAkWmaH5VtXWI_ZGAgYL8LuMrlRVTgYj9DLvquRdrQhrd936vm1X4_mj_PWkwLt6MdH0wyUJ0dWqD1wmirxshJ2jqsP8Ym2pLQBIxOfDZDFHR4nu7w6zUBVgZ6YEQKStZs_m6rtgrE_MIyJ24xYJoIt-tvtnsZcCTc8k0cDIG2L3Z9fH_YxylZUsEqRIsw',
					'cookie' : """_px_f394gi7Fvmc43dfg_user_id=NjNmZmJjNDAtODI5ZS0xMWViLTljOTAtYTFjYmI1ZmI2Zjhh; _ga=undefined; stockx_seen_ask_new_info=true; stockx_experiments_id=web-739356de-5b6c-494e-95de-ceed2d5c6d8a; language_code=en; stockx_default_sneakers_size=9.5; stockx_user_logged_in=true; stockx_user_shipping_region=US; stockx_market_country=US; _pxvid=33b66d47-cc0c-11eb-9533-0242ac12000a; auth0.ssodata=%22{%5C%22lastUsedConnection%5C%22:%5C%22production%5C%22%2C%5C%22lastUsedSub%5C%22:%5C%22auth0|e72f2c36-61d6-11e7-afa5-128878ebb8b6%5C%22}%22; token=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik5USkNNVVEyUmpBd1JUQXdORFk0TURRelF6SkZRelV4TWpneU5qSTNNRFJGTkRZME0wSTNSQSJ9.eyJodHRwczovL3N0b2NreC5jb20vY3VzdG9tZXJfdXVpZCI6ImU3MmYyYzM2LTYxZDYtMTFlNy1hZmE1LTEyODg3OGViYjhiNiIsImh0dHBzOi8vc3RvY2t4LmNvbS9nYV9ldmVudCI6IkxvZ2dlZCBJbiIsImlzcyI6Imh0dHBzOi8vYWNjb3VudHMuc3RvY2t4LmNvbS8iLCJzdWIiOiJhdXRoMHxlNzJmMmMzNi02MWQ2LTExZTctYWZhNS0xMjg4NzhlYmI4YjYiLCJhdWQiOlsiZ2F0ZXdheS5zdG9ja3guY29tIiwiaHR0cHM6Ly9zdG9ja3gtcHJvZC5hdXRoMC5jb20vdXNlcmluZm8iXSwiaWF0IjoxNjIzNjIzMjk1LCJleHAiOjE2MjM2NjY0OTUsImF6cCI6Ik9WeHJ0NFZKcVR4N0xJVUtkNjYxVzBEdVZNcGNGQnlEIiwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSJ9.r-4Tf7DUBpdTeM9GxF4vK9Tqr1P83nW7xFYF53ut4h_0uAupz9hVaGpkqJeOF0dX1fIPuB6jmi3oCYsTTuwt3IWJM6vuI9eYTPuYfSl06ZPfpSCQoqdMWbNe5HEUnkvJ8AZEwcChOQKCTEAS4aLoAIBUWAkWmaH5VtXWI_ZGAgYL8LuMrlRVTgYj9DLvquRdrQhrd936vm1X4_mj_PWkwLt6MdH0wyUJ0dWqD1wmirxshJ2jqsP8Ym2pLQBIxOfDZDFHR4nu7w6zUBVgZ6YEQKStZs_m6rtgrE_MIyJ24xYJoIt-tvtnsZcCTc8k0cDIG2L3Z9fH_YxylZUsEqRIsw; stockx_session=2efc5257-58b3-4de5-b54a-481d32ba0d15; LSKey[c]nf_session={"affinityToken":"","agentname":"Let's Chat","clientPollTimeout":"","id":"","isOldSession":false,"key":"","lastloggedinstatus":false,"magentotext":"e72f2c36-61d6-11e7-afa5-128878ebb8b6","timestamp":1623626603566,"userloggedin":true,"visitor":"","visitormail":"cez.rata1@gmail.com"}; stockx_homepage=sneakers; _px_7125205957_cs=eyJpZCI6IjUwMzcxYmEwLWNjOWUtMTFlYi1hNmU1LWZkNGI2NDdjMjg2ZCIsInN0b3JhZ2UiOnt9LCJleHBpcmF0aW9uIjoxNjIzNjI4OTM4Mzk5fQ==; _dd_s=rum=0&expire=1623628040733; stockx_selected_currency=USD; stockx_product_visits=45; loggedIn=e72f2c36-61d6-11e7-afa5-128878ebb8b6""",
					'if-none-match' : 'W/"82e-pnqoqspvQ4uJ9gOf0PCTofUmjUw"',
					'referer' : 'https://stockx.com/air-jordan-1-retro-high-hyper-royal-smoke-grey',
					'sec-ch-ua' : '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
					'sec-ch-ua-mobile' : '?0',
					'sec-fetch-dest' : 'empty',
					'sec-fetch-mode' : 'cors',
					'sec-fetch-sote' : 'same-origin',
					'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
					'x-requested-with' : 'XMLHttpRequest'
	}

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
	print(url)

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



shoe_names = get_shoe_names()
data = get_sku_id_and_release_date(shoe_names)
get_price_data(data)


