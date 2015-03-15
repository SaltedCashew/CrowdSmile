#!/usr/bin/env python3

# usage: python3 HistoricalDataRequest.py <host-ip>

import argparse
import json
import ssl
import sys
import urllib.request




#TESTING PURPOSES
# data = {
#     "securities": [ "UKEW322 Index"],
#     "fields": ["PX_LAST"],
#     "startDate": "20070101",
#     "endDate": "20140101",
# }

#Liverpool, London, Norfolk, Ipswich, Newcastle, Birmingham, Warwick, Manchester

#AVERAGE SALARY DATA
# data = {
#     "securities": [ "UKEW322 Index", "UKEW116 Index", "UKEW111 Index", "UKEW106 Index", 
#         "UKEW210 Index", "UKEW221 Index", "UKEW220 Index", "UKEW299 Index"],
#     "fields": ["PX_LAST"],
#     "startDate": "20110101",
#     "endDate": "20140101",
#     "periodicitySelection": "MONTHLY"
# }


#MARKET DATA
# data = {
#     "securities": [ "UKX INDEX", "SPX INDEX", "CCMP INDEX", "INDU INDEX", "SX5E INDEX"],
#     "fields": ["PX_LAST"],
#     "startDate": "20150201",
#     "endDate": "20150301",
#     "periodicitySelection": "DAILY"
# }


#UNEMPLOYEMENT DATA
# data = {
#     "securities": [ "UKURLL Index","UKUREC Index","UKURNO Index","UKURIP Index","UKURNE Index"
#         "UKURBH Index","UKURWR Index","UKURME Index"],
#     "fields": ["PX_LAST"],
#     "startDate": "20060101",
#     "endDate": "20080101",
# }


#WEATHER DATA
data = {
    "securities": [ "WEUKEGGP Index","WEUKEGLL Index","WEUKEGGD Index","WER5IPSW Index","WEUKEGNT Index", "WEUKEGGB Index",
        "WEAUWARW Index", "WEUKEGCC Index"],
    "fields": ["PX_LAST"],
    "startDate": "20140101",
    "endDate": "20140301",
}



def request(args):
    req = urllib.request.Request('https://{}/request?ns=blp&service=refdata&type=HistoricalDataRequest'.format(args.host))
    req.add_header('Content-Type', 'application/json')

    ctx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    ctx.load_verify_locations('bloomberg.crt')
    ctx.load_cert_chain('client.crt', 'client.key')

    https_sslv23_handler = urllib.request.HTTPSHandler(context=ctx)
    opener = urllib.request.build_opener(https_sslv23_handler)
    urllib.request.install_opener(opener)

    try:
        res = opener.open(req, data=json.dumps(data).encode("ascii"))
        #print(res.read())

        decodejson=json.loads(res.read().decode('utf-8'))
        
        i=0
        for key in decodejson:
               
            print(decodejson['data'][0]['securityData']['fieldData'][i]['PX_LAST'])
            i=i+1
 
    except Exception as e:
        e
        print(e)
        return 1
    return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('host', type=str)
    return request(parser.parse_args())

if __name__ == "__main__":
    sys.exit(main())