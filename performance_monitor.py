import requests
import urllib
import time
import json
import csv


def get_token(config, req):
    if req is None:
        username = config['username']
        password = config['password']
    else:
        username = req['username']
        password = req['password']
    tokenurl = config['tokenurl'] + "?username=" + username + "&password=" + password
    return requests.get(tokenurl).text

def get_avg_time(times):
    return format(sum(times) / len(times))

#Open output file
with open('output.csv', 'wb') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter=';',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    csvwriter.writerow(['request', 'response time', 'response time + content'])

    #Read requests from settings
    with open('settings.json', 'r') as f:
        config = json.load(f)
        stdtoken = get_token(config, None)

        #Get response time for each request
        for req in config['requests']:
            responsetimes = []
            responsetimeswithcontent = []

            url = config['domainurl'] + req['url']
            print 'Requesting ' + req['url']
            if req.get('username') is None:
                headers = {'Authorization': 'SAML ' + stdtoken }
            else:
                token = get_token(config, req)
                headers = {'Authorization': 'SAML ' + token }

            r = requests.get(url, headers=headers)
            for i in range(config['repetitions']):
                start = time.time()
                r = requests.get(url, headers=headers)
                end = time.time() - start
                responsetimes.append(r.elapsed.total_seconds())
                responsetimeswithcontent.append(end)

            responsetimeavg = get_avg_time(responsetimes)
            responsetimeswithcontentavg = get_avg_time(responsetimeswithcontent)

            csvwriter.writerow([req['url'], responsetimeavg, responsetimeswithcontentavg])
