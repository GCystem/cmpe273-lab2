
from spyne import Application, rpc, ServiceBase, Iterable, Integer, Unicode, srpc

from spyne.protocol.json import JsonDocument

from spyne.protocol.http import HttpRpc
from spyne.server.wsgi import WsgiApplication
from datetime import datetime
import re
import urllib3
import simplejson as json

class CrimeReport(ServiceBase):
    @srpc(float, float, float, _returns=Iterable(Unicode))
    def checkcrime(lat, lon, radius):
        http = urllib3.PoolManager()
        crime_url = 'https://api.spotcrime.com/crimes.json?lat=%f&lon=%f&radius=%f&key=.' % (lat, lon, radius)

        r = http.request('GET', crime_url)
        report = json.loads(r.data)
        #yield report['crimes']
        crimes = report['crimes']
        crime_type_count = dict()
        event_time_count = {
            "12:01am-3am" : 0,
            "3:01am-6am" : 0,
            "6:01am-9am" : 0,
            "9:01am-12noon" : 0,
            "12:01pm-3pm" : 0,
            "3:01pm-6pm" : 0,
            "6:01pm-9pm" : 0,
            "9:01pm-12midnight" : 0
        } 
        crime_street_count = dict()
        count = 0
        for crime in crimes:
            
            count += 1 
            if crime_type_count.has_key(crime['type']) == False:
                crime_type_count[crime['type']] = 1

            else:
                crime_type_count[crime['type']] += 1

            crime_time = datetime.strptime(crime['date'], "%m/%d/%y %I:%M %p").time()
            slot1 = datetime.strptime('12:01am', "%I:%M%p").time()
            slot2 = datetime.strptime('03:00am', "%I:%M%p").time()
            slot3 = datetime.strptime('03:01am', "%I:%M%p").time()
            slot4 = datetime.strptime('06:00am', "%I:%M%p").time()
            slot5 = datetime.strptime('06:01am', "%I:%M%p").time()
            slot6 = datetime.strptime('09:00am', "%I:%M%p").time()
            slot7 = datetime.strptime('09:01am', "%I:%M%p").time()
            slot8 = datetime.strptime('12:00pm', "%I:%M%p").time()
            slot9 = datetime.strptime('12:01pm', "%I:%M%p").time()
            slot10 = datetime.strptime('03:00pm', "%I:%M%p").time()
            slot11 = datetime.strptime('03:01pm', "%I:%M%p").time()
            slot12 = datetime.strptime('06:00pm', "%I:%M%p").time()
            slot13 = datetime.strptime('06:01pm', "%I:%M%p").time()
            slot14 = datetime.strptime('09:00pm', "%I:%M%p").time()
            slot15 = datetime.strptime('09:01pm', "%I:%M%p").time()
            slot16 = datetime.strptime('12:00am', "%I:%M%p").time()
            
            if crime_time >= slot1 and crime_time <= slot2:
                event_time_count['12:01am-3am'] += 1
            elif crime_time >= slot3 and crime_time <= slot4:
                event_time_count['3:01am-6am'] += 1
            elif crime_time > slot5 and crime_time <= slot6:
                event_time_count['6:01am-9am'] += 1
            elif crime_time > slot7 and crime_time <= slot8:
                event_time_count['9:01am-12noon'] += 1
            elif crime_time > slot9 and crime_time <= slot10:
                event_time_count['12:01pm-3pm'] += 1
            elif crime_time > slot11 and crime_time <= slot12:
                event_time_count['3:01pm-6pm'] += 1
            elif crime_time > slot13 and crime_time <= slot14:
                event_time_count['6:01pm-9pm'] += 1
            elif crime_time > slot15 or crime_time == slot16:
                event_time_count['9:01pm-12midnight'] += 1
            
            # ST, AV, DR, RD, LN, WY, LP, CT, PL
            #yield crime['address']
            regex = r'(\b\w\b)*\s*([\d\w])*\s*([\d\w])+\s+((ST\Z)|(AV\Z)|(DR\Z)|(RD\Z)|(LN\Z)|(WY\Z)|(LP\Z)|(CT\Z)|(BLVD\Z)|(PL\Z))+'
            crime_address = re.search(regex, crime['address'], re.I)
            if crime_address:
                #yield crime['address']
                #yield crime_address.group()
                adsstr = str(crime_address.group())
                adsstr = adsstr.lstrip()
                adsstr = adsstr.replace('OF', '').lstrip()
                #yield adsstr
                if crime_street_count.has_key(adsstr) == False:
                    crime_street_count[adsstr] = 1

                else:
                    crime_street_count[adsstr] += 1
            
            regex = r'(\w\b)*\s*([\d\w])*\s*([\d\w])+\s+((ST\b)|(AV\b)|(DR\b)|(RD\b)|(LN\b)|(WY\b)|(LP\b)|(CT\b)|(BLVD\Z)|(PL\b))+\s+&+'    
            crime_address_and = re.search(regex, crime['address'], re.I)
            if crime_address_and:
                adsstr2 = str(crime_address_and.group())
                adsstr2 = adsstr2.lstrip()
                adsstr2 = adsstr2.replace('&', '').rstrip()
                if crime_street_count.has_key(adsstr2) == False:
                    crime_street_count[adsstr2] = 1
                else:
                    crime_street_count[adsstr2] += 1         

        crime_street_sort = sorted(crime_street_count, key=crime_street_count.get, reverse=True)
        crime_street_sort = crime_street_sort[:3]

        yield {"total_crime": count, "the_most_dangerous_streets": crime_street_sort, "crime_type_count": crime_type_count, "event_time_count":event_time_count}
        

application = Application([CrimeReport],
    tns='spyne.examples.hello',
    in_protocol=HttpRpc(validator='soft'),
    out_protocol=JsonDocument()
)
if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    wsgi_app = WsgiApplication(application)
    server = make_server('0.0.0.0', 8000, wsgi_app)
    server.serve_forever()