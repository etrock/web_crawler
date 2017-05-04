# -*- coding: utf-8 -*-
import re
import sys
import requests
from optparse import OptionParser
from requests.exceptions import ConnectionError
from multiprocessing.dummy import Pool as ThreadPool

import time


class Options(object):
    """Main options and command line options."""

    def __init__(self):
        self._commandLineOptions = self._parseCommandLine()

        self.links = self._commandLineOptions.links
        self.threadNumber = self._commandLineOptions.threadNumber


    def _parseCommandLine(self):

    	#check if the threadNumber is an integer or not
    	def checkThreadNumber(option, dummy_opt_str, value, parser):
            if not int(value):
                errStr = "The thread number is not valid!"
                print errStr
            else:
                infoStr = "Thread number: " + str(value)
                print infoStr
            setattr(parser.values, option.dest, value)

        def checkLinks(option, dummy_opt_str, value, parser):
            if len(value) <5:
                errStr = "The links is not valid!"
                print errStr
            else:
                infoStr = "The links: '%s' " % value
                print infoStr

            #make a list from links
            if ',' in value:
            	value = value.split(',')
            else:
            	value = [value]

            #if link don't contains the protocal set to http:// 
            i = 0
            while i < len(value):
            	if "http:" not in value[i] and "https:" not in value[i]:
            		value[i] = "http://"+value[i]
            	i += 1
            setattr(parser.values, option.dest, value)

    	parser = OptionParser()

    	parser.add_option("-l","--links", action="callback", callback=checkLinks, type="string",
                          dest="links",
                          help='"Give some links and use comma to separate them"')

    	parser.add_option("-t", "--threads", action="callback", callback=checkThreadNumber, type="int",
                          dest="threadNumber", help="Tread Number")

    	_result, args = parser.parse_args()
        return _result

def check_link(url):
	#send the requests
	try: 
		r = requests.get(url)
		if 'content-length' in r.headers.keys() or 'Content-Length' in r.headers.keys():
			print str(r.status_code)  +" : "+  url + " : " + r.headers['content-length']
		else:
			print str(r.status_code)  +" : "+  url + " : " + str(len(r.content))
		#get the content
		data = r.content
	except ConnectionError as e:    # This is the correct syntax
   		print e
   		r = "No response"
   		data = ""
	#print the status_code url and size
	
	return data.decode('utf8')

def get_links(url):
    """Scan the text for http URLs and return a set
    of URLs found, without duplicates"""
    
    #get the content of page
    text = check_link(url)
    
    # look for any http URL in the page
    links = []
    host = url.split('.')[1]
    #print "host: "+host
    urlpattern = r"(.*?\s*(href=)\"(.*?)\".*?>(.*?))"
    
    matches = re.findall(urlpattern, text)
    for match in matches:
    	href = match[2]
    	# if the link is / or # continue with next link
        if match[2] == '/' or match[2] =='#':
            continue
        # if the last part contains %,?,. cut down
        if href != url and ('?' in href.split('/')[-1] or '.' in href.split('/')[-1] or '%' in href.split('/')[-1]):
        	href = '/'.join(href.split('/')[:-1])
        # if start with http or www and the link contains the host we add to links array
        if ( href.startswith('http') or href.startswith('www') ) and host in href:
            if href not in links:
                links.append(href)
        # if not contains host thats mean its a different url we continue with the next url
        elif (href.startswith('http') or href.startswith('www') ) and host not in href:
            continue
        else:
            if url+href not in links:
                links.append(url+href)
    return links

def run_crawler(link):
	globalLinks = [link.decode('unicode-escape')]
	i = 0
	while i < len(globalLinks):
		globalLinks.extend(get_links(globalLinks[i]))
		i +=1
		#print globalLinks
	return True

def main():
	#get options links and threadNumber
	options = Options()

	# Make the Pool of workers
	pool = ThreadPool(options.threadNumber)

	# Open the urls in their own threads
	# and return the results
	results = pool.map(run_crawler, options.links)

	#close the pool and wait for the work to finish 
	pool.close() 
	pool.join()
		



if __name__ == '__main__':
    print "Python version: " + sys.version
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))