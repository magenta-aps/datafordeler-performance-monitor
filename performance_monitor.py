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
with open('output.csv', 'wb') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter=';',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    csvwriter.writerow(['request', 'response time', 'response time + content'])

    #Read requests from settings
    with open('settings.json', 'r') as f:
        config = json.load(f)
        repetitions = range(config['repetitions'])
        stdheaders = get_tokenheader(config, None)

        #Get response time for load balancer
        url = config['touchurl']
        lb_timeavg, lb_timeavg_cont = get_response_time(url, stdheaders, repetitions)
        csvwriter.writerow(["to loadbalancer", lb_timeavg, lb_timeavg_cont])

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
            csvwriter.writerow([url, timeavg, timeavg_cont])
