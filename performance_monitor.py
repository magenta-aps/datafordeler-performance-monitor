import requests
import time
import json
import csv


def get_tokenheader(config, req):
    if req is None:
        username = config['username']
        password = config['password']
    else:
        username = req['username']
        password = req['password']
    tokenurl = config['tokenurl'] + "?username=" + username + "&password=" + password
    token = requests.get(tokenurl).text
    return {'Authorization': 'SAML ' + token }

def get_avg_time(times):
    return sum(times) / len(times)

def get_response_time(url, headers, repetitions):
    responsetimes = []
    responsetimeswithcontent = []
    r = requests.get(url, headers=headers)

    for i in repetitions:
        print 'Requesting iteration #' + str(i)
        start = time.time()
        r = requests.get(url, headers=headers)
        end = time.time() - start
        responsetimes.append(r.elapsed.total_seconds())
        responsetimeswithcontent.append(end)

    responsetimeavg = get_avg_time(responsetimes)
    responsetimewithcontentavg = get_avg_time(responsetimeswithcontent)
    return responsetimeavg, responsetimewithcontentavg

#Open output file

headerexists = False
try:
    with open('output.csv', 'r') as csvfile:
        for line in csvfile:
            if len(line.strip()) > 0:
                headerexists = True
                break
except IOError:
    pass

with open('output.csv', 'a') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter=';',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    if not headerexists:
        csvwriter.writerow(['date', 'request', 'response time', 'response time + content'])
    now = time.strftime("%Y.%m.%d %H:%M:%S", time.localtime(time.time()))

    #Read requests from settings
    with open('settings.json', 'r') as f:
        config = json.load(f)
        repetitions = range(config['repetitions'])
        stdheaders = get_tokenheader(config, None)

        #Get response time for load balancer
        url = config['touchurl']
        lb_timeavg, lb_timeavg_cont = get_response_time(url, stdheaders, repetitions)
        csvwriter.writerow([now, "to loadbalancer", lb_timeavg, lb_timeavg_cont])

        #Get response time for each request
        for req in config['requests']:
            url = config['domainurl'] + req['url']
            if req.get('username') is None:
                headers = stdheaders
            else:
                headers = get_tokenheader(config, req)
            print 'Requesting ' + url
            timeavg, timeavg_cont = get_response_time(url, headers, repetitions)
            timeavg = format(timeavg - lb_timeavg)
            timeavg_cont = format(timeavg_cont - lb_timeavg_cont)
            csvwriter.writerow([now, url, timeavg, timeavg_cont])

