# usage: python3 HistoricalDataRequest.py <host-ip>

import argparse
import json
import ssl
import sys
import urllib.request

citydict={'Liverpool':['UKEW322 Index', 'UKURLL Index','WEUKEGGP Index','UKX Index','SX5E Index','CCMP Index','INDU Index','SPX Index'],
'London':['UKEW116 Index', 'UKUREC Index','WEUKEGLL Index','UKX Index','SX5E Index','CCMP Index','INDU Index','SPX Index'],
'Norfolk':['UKEW111 Index', 'UKURNO Index','WEUKEGGD Index','UKX Index','SX5E Index','CCMP Index','INDU Index','SPX Index'],
'Ipswich':['UKEW106 Index', 'UKURIP Index','WER5IPSW Index', 'UKX Index','SX5E Index','CCMP Index','INDU Index','SPX Index'],
'Newcastle':['UKEW210 Index', 'UKURNE Index','WEUKEGNT Index','UKX Index','SX5E Index','CCMP Index','INDU Index','SPX Index'],
'Birmingham':['UKEW221 Index', 'UKURBH Index','WEUKEGBB Index','UKX Index','SX5E Index','CCMP Index','INDU Index','SPX Index'],
'Warwick':['UKEW220 Index', 'UKURWR Index','WEAUWARW Index','UKX Index','SX5E Index','CCMP Index','INDU Index','SPX Index'],
'Manchester':['UKEW299 Index', 'UKURME Index','WEUKEGCC Index','UKX Index','SX5E Index','CCMP Index','INDU Index','SPX Index']}


def request(data):
    str=''
    req = urllib.request.Request('https://{}/request?ns=blp&service=refdata&type=HistoricalDataRequest'.format('http-api.openbloomberg.com'))
    req.add_header('Content-Type', 'application/json')

    ctx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    ctx.load_verify_locations('bloomberg.crt')
    ctx.load_cert_chain('client.crt', 'client.key')

    https_sslv23_handler = urllib.request.HTTPSHandler(context=ctx)
    opener = urllib.request.build_opener(https_sslv23_handler)
    urllib.request.install_opener(opener)

    try:
        res = opener.open(req, data=json.dumps(data).encode("ascii"))
        #f.write(res.read().decode('utf-8'))
        str=res.read().decode('utf-8')
    except Exception as e:
        e
        print(e)

    return str

def analyseSalarydata(str):
    result=0.0
    decodejson = json.loads(str)  
    high=0.0
    low=1000000.0
    
    #print(str)
    arraylen=len(decodejson['data'][0]['securityData']['fieldData'])
    n=0
    while (n<arraylen):
        salary=decodejson['data'][0]['securityData']['fieldData'][n]['PX_LAST']
        if(salary>high):
            high=salary
        if (salary<low):
            low=salary
            
        n=n+1
    
    result=(salary-low)/(high-low)
    if result<0.0:
        result=0.0
    else:
        if result>1.0:
            result=1.0

    #print(low, high, result)
    return result

def analyseUnemploymentdata(str):
    result=0.0
    decodejson = json.loads(str)  
    high=0.0
    low=1000000.0
    
    #print(str)
    arraylen=len(decodejson['data'][0]['securityData']['fieldData'])
    n=0
    while (n<arraylen):
        unemployment=decodejson['data'][0]['securityData']['fieldData'][n]['PX_LAST']
        if(unemployment>high):
            high=unemployment
        if (unemployment<low):
            low=unemployment
            
        n=n+1
    
    result=(unemployment-low)/(high-low)
    result=1-result
    if result<0.0:
        result=0.0
    else:
        if result>1.0:
            result=1.0

    #print(low, high, result)
    return result

def analyseWeatherdata(str):
    result=0.0
    decodejson = json.loads(str)
    average=0.0
    
    #print(str)
    arraylen=len(decodejson['data'][0]['securityData']['fieldData'])
    n=0
    while (n<arraylen):
        average=average+decodejson['data'][0]['securityData']['fieldData'][n]['PX_LAST']
        n=n+1
        
    average=average/arraylen

    result = abs((average-20.0)/20.0)
    result=1-result    
    if result<0.0:
        result=0.0
    else:
        if result>1.0:
            result=1.0    
          
    #print(average, result)
    return result

def analyseStockdata(str):
    result=0.0
    decodejson = json.loads(str)  
    high=0.0
    low=1000000.0
    
    #print(str)
    arraylen=len(decodejson['data'][0]['securityData']['fieldData'])
    n=0
    while (n<arraylen):
        price=decodejson['data'][0]['securityData']['fieldData'][n]['PX_LAST']
        if(price>high):
            high=price
        if (price<low):
            low=price
            
        n=n+1
    
    result=(price-low)/(high-low)
    if result<0.0:
        result=0.0
    else:
        if result>1.0:
            result=1.0

    #print(low, high, result)
    return result


def cityanalysis(cityname):
    percentage=0.0
    if cityname in citydict:
        salarydata = {
            "securities": [citydict[cityname][0]],
            "fields": ["PX_LAST"],
            "startDate": "20040301",
            "endDate": "20140301",
            "periodicitySelection": "YEARLY"
        }
        
        str=request(salarydata)
        percentage=percentage+0.3*analyseSalarydata(str)
        
        unemploymentdata = {
            "securities": [citydict[cityname][1]],
            "fields": ["PX_LAST"],
            "startDate": "20020301",
            "endDate": "20080301",
            "periodicitySelection": "YEARLY"
        }
        str=request(unemploymentdata)
        percentage=percentage+0.4*analyseUnemploymentdata(str)
        
        weatherdata = { 
            "securities": [citydict[cityname][2]],
            "fields": ["PX_LAST"],
            "startDate": "20150301",
            "endDate": "20150315",
            "periodicitySelection": "DAILY"
        }
        
        str=request(weatherdata)
        percentage=percentage+0.25*analyseWeatherdata(str)
        
        stock1data = {
            "securities": [citydict[cityname][3]],
            "fields": ["PX_LAST"],
            "startDate": "20150215",
            "endDate": "20150315",
            "periodicitySelection": "DAILY"
        }
        
        str=request(stock1data)
        percentage=percentage+0.1*analyseStockdata(str) 
        
        stock2data = {
            "securities": [citydict[cityname][4]],
            "fields": ["PX_LAST"],
            "startDate": "20150215",
            "endDate": "20150315",
            "periodicitySelection": "DAILY"
        }
        
        str=request(stock2data)
        percentage=percentage+0.05*analyseStockdata(str)     

        stock3data = {
            "securities": [citydict[cityname][5]],
            "fields": ["PX_LAST"],
            "startDate": "20150215",
            "endDate": "20150315",
            "periodicitySelection": "DAILY"
        }
        
        str=request(stock3data)
        percentage=(percentage+0.005*analyseStockdata(str))
        
        stock4data = {
            "securities": [citydict[cityname][6]],
            "fields": ["PX_LAST"],
            "startDate": "20150215",
            "endDate": "20150315",
            "periodicitySelection": "DAILY"
        }
        
        str=request(stock4data)
        percentage=percentage+0.005*analyseStockdata(str) 
        
        stock5data = {
            "securities": [citydict[cityname][7]],
            "fields": ["PX_LAST"],
            "startDate": "20150215",
            "endDate": "20150315",
            "periodicitySelection": "DAILY"
        }
        
        str=request(stock5data)
        percentage=percentage+0.005*analyseStockdata(str) 
        
    # print(percentage)
    return percentage

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('host', type=str)

    parser = 'http-api.openbloomberg.com';
    
    return cityanalysis('Newcastle')

    

if __name__ == "__main__":
    sys.exit(main())


