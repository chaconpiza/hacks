
from datetime import datetime

def _normalize_timestamp(timestamp):
    d = None
    if timestamp and len(timestamp) >= 10:
        try:
            d = datetime.strptime(timestamp[0:10], '%Y-%m-%d')
        except ValueError as e:
            print "Unable to parse timestamp '%s' - %s" % (timestamp, str(e))
    if not d:
        d = datetime.today()
    return d.strftime('%Y-%m-%d')

print _normalize_timestamp('12345678912')

print _normalize_timestamp('1980-07-15')

print _normalize_timestamp('2018-09-27T12:03:34Z')
