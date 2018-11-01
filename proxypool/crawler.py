import json
import re
from .utils import get_page
from pyquery import PyQuery as pq


class ProxyMetaclass(type):
	def __new__(cls, name, bases, attrs):
		count = 0
		attrs['__CrawlFunc__'] = []
		for k, v in attrs.items():
			if 'crawl_' in k:
				attrs['__CrawlFunc__'].append(k)
				count += 1
		attrs['__CrawlFuncCount__'] = count
		return type.__new__(cls, name, bases, attrs)


class Crawler(object, metaclass=ProxyMetaclass):
	def get_proxies(self, callback):
		proxies = []
		for proxy in eval("self.{}()".format(callback)):
			print('成功获取到代理', proxy)
			proxies.append(proxy)
		return proxies

	def crawl_daili66(self, page_count=4):
		"""
		获取代理66
		:param page_count: 页码
		:return: 代理
		"""
		start_url = 'http://www.66ip.cn/{}.html'
		urls = [start_url.format(page) for page in range(2, page_count + 1)]
		for url in urls:
			print('Crawling', url)
			html = get_page(url)
			if html:
				doc = pq(html)
				trs = doc('.containerbox table tr:gt(0)').items()
				for tr in trs:
					ip = tr.find('td:nth-child(1)').text()
					port = tr.find('td:nth-child(2)').text()
					yield ':'.join([ip, port])

	def crawl_daili66_page1(self):
		"""
		获取代理66的page1
		:return: 代理
		"""
		start_url = 'http://www.66ip.cn/'
		html = get_page(start_url)
		if html:
			doc = pq(html)
			trs = doc('.containerbox table tr:gt(0)').items()
			for tr in trs:
				ip = tr.find('td:nth-child(1)').text()
				port = tr.find('td:nth-child(2)').text()
				yield ':'.join([ip, port])

	def crawl_daili66_API(self, num=100):
		"""
		获取代理66的API
		:return: 代理
		"""
		start_url = 'http://www.66ip.cn/nmtq.php?getnum={num}&isp=0&anonymoustype={page}&start=&ports=&export=&ipaddress=&area=0&proxytype=2&api=66ip'
		urls = [start_url.format(num=num, page=page) for page in [3, 4]]
		for url in urls:
			html = get_page(url)
			if html:
				poxy_list = re.findall(r'\d*.\d*.\d*.\d*:\d*', html)
				for poxy in poxy_list:
					yield poxy

	def crawl_goubanjia(self):  # +++++++++++++++++++++++++++++++++++未成熟+++++++++++++++++++++++++++
		"""
		获取Goubanjia
		:return: 代理
		"""
		start_url = 'http://www.goubanjia.com/'
		html = get_page(start_url)
		if html:
			doc = pq(html)
			trs = doc('services > div > div.row > div > div > div > table > tbody > tr').items()
			for tr in trs:
				ip = tr.find('td.ip').text()
				port = tr.find("td.ip > span.port.GEGEI").text()
				yield ':'.join([ip, port])

	def crawl_ip181(self):
		start_url = 'http://www.ip181.com/'
		html = get_page(start_url)
		ip_dict = eval(html)
		if ip_dict["ERRORCODE"] == "0":
			for ip_detial in ip_dict["RESULT"]:
				yield ':'.join([ip_detial['ip'], ip_detial['port']])

	def crawl_ip3366(self, page=4):
		for stype in [1, 3]:
			for page in range(1, page):
				start_url = 'http://www.ip3366.net/free/?stype={stype}&page={page}'.format(stype=stype, page=page)
				html = get_page(start_url)
				ip_address = re.compile('<tr>\s*<td>(.*?)</td>\s*<td>(.*?)</td>')
				# \s * 匹配空格，起到换行作用
				re_ip_address = ip_address.findall(html)
				for address, port in re_ip_address:
					result = address + ':' + port
					yield result.replace(' ', '')

	def crawl_ip3366_API(self, page=4):
		for i in range(1, page):
			start_url = 'http://www.ip3366.net/?stype=1&page={}'.format(i)
			html = get_page(start_url)
			if html:
				find_tr = re.compile('<tr>(.*?)</tr>', re.S)
				trs = find_tr.findall(html)
				for s in range(1, len(trs)):
					find_ip = re.compile('<td>(\d+\.\d+\.\d+\.\d+)</td>')
					re_ip_address = find_ip.findall(trs[s])
					find_port = re.compile('<td>(\d+)</td>')
					re_port = find_port.findall(trs[s])
					for address, port in zip(re_ip_address, re_port):
						address_port = address + ':' + port
						yield address_port.replace(' ', '')

	def crawl_premproxy(
			self):  # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++国外代理国内登不上++++++++++++++++++++++++++++++++++++++++++
		for i in ['China-01', 'China-02', 'China-03', 'China-04', 'Taiwan-01']:
			start_url = 'https://premproxy.com/proxy-by-country/{}.htm'.format(i)
			html = get_page(start_url)
			if html:
				ip_address = re.compile('<td data-label="IP:port ">(.*?)</td>')
				re_ip_address = ip_address.findall(html)
				for address_port in re_ip_address:
					yield address_port.replace(' ', '')

	def crawl_xroxy(
			self):  # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++国外代理国内登不上++++++++++++++++++++++++++++++++++++++++++
		for i in ['CN', 'TW']:
			start_url = 'https://www.xroxy.com/free-proxy-lists/?port=&type=&ssl=&country={}'.format(i)
			html = get_page(start_url)
			if html:
				ip_address1 = re.compile("title='View this Proxy details'>\s*(.*).*")
				re_ip_address1 = ip_address1.findall(html)
				ip_address2 = re.compile("title='Select proxies with port number .*'>(.*)</a>")
				re_ip_address2 = ip_address2.findall(html)
				for address, port in zip(re_ip_address1, re_ip_address2):
					address_port = address + ':' + port
					yield address_port.replace(' ', '')

	def crawl_kuaidaili(self, page=4):
		for i in range(1, page):
			start_url = 'http://www.kuaidaili.com/free/inha/{}/'.format(i)
			html = get_page(start_url)
			if html:
				ip_address = re.compile('<td data-title="IP">(.*?)</td>')
				re_ip_address = ip_address.findall(html)
				port = re.compile('<td data-title="PORT">(.*?)</td>')
				re_port = port.findall(html)
				for address, port in zip(re_ip_address, re_port):
					address_port = address + ':' + port
					yield address_port.replace(' ', '')

	def crawl_xicidaili(self, page=3):
		for i in range(1, page):
			start_url = 'http://www.xicidaili.com/nn/{}'.format(i)
			headers = {
				'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
				'Cookie': '_free_proxy_session=BAh7B0kiD3Nlc3Npb25faWQGOgZFVEkiJWRjYzc5MmM1MTBiMDMzYTUzNTZjNzA4NjBhNWRjZjliBjsAVEkiEF9jc3JmX3Rva2VuBjsARkkiMUp6S2tXT3g5a0FCT01ndzlmWWZqRVJNek1WanRuUDBCbTJUN21GMTBKd3M9BjsARg%3D%3D--2a69429cb2115c6a0cc9a86e0ebe2800c0d471b3',
				'Host': 'www.xicidaili.com', 'Referer': 'http://www.xicidaili.com/nn/3',
				'Upgrade-Insecure-Requests': '1', }
			html = get_page(start_url, options=headers)
			if html:
				find_trs = re.compile('<tr class.*?>(.*?)</tr>', re.S)
				trs = find_trs.findall(html)
				for tr in trs:
					find_ip = re.compile('<td>(\d+\.\d+\.\d+\.\d+)</td>')
					re_ip_address = find_ip.findall(tr)
					find_port = re.compile('<td>(\d+)</td>')
					re_port = find_port.findall(tr)
					for address, port in zip(re_ip_address, re_port):
						address_port = address + ':' + port
						yield address_port.replace(' ', '')

	def crawl_iphai(self):
		for end in ['free/wg/', 'free/ng/', '']:
			start_url = 'http://www.iphai.com/{}'.format(end)
			html = get_page(start_url)
			if html:
				find_tr = re.compile('<tr>(.*?)</tr>', re.S)
				trs = find_tr.findall(html)
				for s in range(1, len(trs)):
					re_ip_address = re.findall(r'<td>\s+(\d+\.\d+\.\d+\.\d+)\s+</td>',trs[s], re.S)
					find_port = re.compile('<td>\s+(\d+)\s+</td>', re.S)
					re_port = find_port.findall(trs[s])
					for address, port in zip(re_ip_address, re_port):
						address_port = address + ':' + port
						yield address_port.replace(' ', '')

	def crawl_89ip(self):
		start_url = 'http://www.89ip.cn/tqdl.html?api=1&num=100&port=&address=&isp='
		html = get_page(start_url)
		if html:
			g = re.findall(r'(\d+\.\d+\.\d+\.\d+:\d+)',html, re.S)
			for ip_single in g:
				yield ip_single

	def crawl_data5u(self):
		for tag in ['gngn/', '', 'gnpt/', 'gwgn/', 'gwpt/']:
			start_url = 'http://www.data5u.com/free/{tag}index.shtml'.format(tag=tag)
			headers = {
				'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
				'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
				'Cache-Control': 'max-age=0', 'Connection': 'keep-alive',
				'Cookie': 'JSESSIONID=47AA0C887112A2D83EE040405F837A86', 'Host': 'www.data5u.com',
				'Referer': 'http://www.data5u.com/free/index.shtml', 'Upgrade-Insecure-Requests': '1',
				'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36', }
			html = get_page(start_url, options=headers)
			g = re.findall(r'<span><li>(\d+\.\d+\.\d+\.\d+)</li>.*?<li class=\"port.*?>(\d+)</li>',html, re.S)
			for ip_single in g:
				yield ':'.join([ip_single[0], ip_single[1]])

	def crawl_3464(self):
		start_url = 'http://www.3464.com/data/Proxy/http/'
		html = get_page(start_url)
		g = re.findall(r'<tr><td>(\d+\.\d+\.\d+\.\d+)</td><td>(\d+)</td><td>', html)
		for ip_single in g:
			yield ':'.join([ip_single[0], ip_single[1]])

	def crawl_a2u(
			self):  # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++好代理+++++++++++++++++++++++++++++++++++++++++++++
		start_url = 'https://raw.githubusercontent.com/a2u/free-proxy-list/master/free-proxy-list.txt'
		text = get_page(start_url)
		ip_lists = re.findall(r'\d+\.\d+\.\d+\.\d+:\d+', text)
		for ip in ip_lists:
			yield ip

	def crawl_ihuan(self):
		for tage in ['', 'address/5Lit5Zu9.html', 'address/6aaZ5riv.html', 'address/576O5Zu9.html']:
			start_url = 'https://ip.ihuan.me/{}'.format(tage)
			html = get_page(start_url)
			g = re.findall(r'>(\d+\.\d+\.\d+\.\d+)</a></td><td>(\d+)</td><td>', html)
			for ip_single in g:
				yield ':'.join([ip_single[0], ip_single[1]])

	def crawl_seofangfa(self):
		start_url = 'http://ip.seofangfa.com/'
		html = get_page(start_url)
		g = re.findall(r'<tr><td>(\d+\.\d+\.\d+\.\d+)</td><td>(\d+)</td><td>', html)
		for ip_single in g:
			yield ':'.join([ip_single[0], ip_single[1]])

	def crawl_wndaili(self, page=10):
		for i in range(1, page):
			start_url = 'http://wndaili.cn/?page={}'.format(i)
			html = get_page(start_url)
			g = re.findall(r'<tr>\s*<td>(.*?)</td>\s*<td>(.*?)</td>', html)
			for ip_single in g:
				yield ':'.join([ip_single[0], ip_single[1]])

	def crawl_clarketm(self):
		start_url = 'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list.txt'
		text = get_page(start_url)
		ip_lists = re.findall(r'\d+\.\d+\.\d+\.\d+:\d+', text)
		for ip in ip_lists:
			yield ip

	def crawl_sunny9577(self):
		start_url = 'https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.json'
		text = get_page(start_url)
		ip_list =re.findall(r'"ip":"(\d+\.\d+\.\d+\.\d+)","port":"(\d+)","', text)
		for ip_single in ip_list:
			yield ':'.join([ip_single[0], ip_single[1]])
	#++++++++++++++++++++++++++++++++++++++++++++++++未部署+++++++++++++++++++++++++++++++++++++++++++++++++++++++====

	def crawl_free_proxy_list(self):
		for start_url in ['https://free-proxy-list.net/','https://free-proxy-list.net/uk-proxy.html','https://www.us-proxy.org/','https://www.sslproxies.org/']:
			text = get_page(start_url)
			ip_list = re.findall(r'<td>(\d+\.\d+\.\d+\.\d+)</td><td>(\d+)</td>', text)
			for ip_single in ip_list:
				yield ':'.join([ip_single[0], ip_single[1]])

	def crawl_crossincode(self):
		start_url = 'http://lab.crossincode.com/proxy/'
		text = get_page(start_url)
		ip_list = re.findall(r'<tr>\s*<td>(\d+\.\d+\.\d+\.\d+)</td>\s*<td>(\d+)</td>',text)
		for ip_single in ip_list:
			yield ':'.join([ip_single[0], ip_single[1]])

	def crawl_jiangxianli(self):
		start_url = 'http://ip.jiangxianli.com/'
		text = get_page(start_url)
		page_list = re.findall(r'<li><a href=".*">(\d*)</a></li>',text)
		ip_list = re.findall(r'<td>(\d+\.\d+\.\d+\.\d+)</td>\s*<td>(\d+)</td>', text)
		for page in page_list:
			text = get_page('http://ip.jiangxianli.com/?page={}'.format(page))
			ip_list.extend(re.findall(r'<td>(\d+\.\d+\.\d+\.\d+)</td>\s*<td>(\d+)</td>', text))
		for ip_single in ip_list:
			yield ':'.join([ip_single[0], ip_single[1]])

	def crawl_cn_proxy(self):
		start_url = 'http://cn-proxy.com/{}'
		for tag in ['','archives/218']:
			text = get_page(start_url.format(tag))
			ip_list = re.findall(r'<tr>\s*<td>(\d+\.\d+\.\d+\.\d+)</td>\s*<td>(\d+)</td>', text)
			for ip_single in ip_list:
				yield ':'.join([ip_single[0], ip_single[1]])

	def crawl_freeproxylists(self,page=10):
		start_url = 'http://www.freeproxylists.net/zh/?page={}'
		for i in range(page):
			text = get_page(start_url.format(page))
			print(text)