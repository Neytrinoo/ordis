###  A sample pygster parser file that can be used to count the number
###  of response codes found in an Apache access log.
###
###  For example:
###  sudo ./pygster --dry-run --output=ganglia SamplePygster /var/log/httpd/access_log
###
###

import csv
import datetime
import dateutil.parser
import simplejson as json
import re
import time
import sys
from StringIO import StringIO

from pygster.pygster_helper import MetricObject, PygsterParser
from pygster.pygster_helper import PygsterParsingException

DATE, TIME, APP, MSG = 2,3,4,5

def total_seconds(td):
    # python2.4 backport: datetime.total_seconds()
    #  NB: need real/float division
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10.0**6

def strptime(date_string):
    return dateutil.parser.parse(date_string)

class ECBasePygsterParser(PygsterParser):
    def parse_line(self, line):
        for data in csv.reader(StringIO(line)):
            if data[APP] != "COMPASS_ECCONNECT":
                continue

            s_logtime = '%s %s' % (data[DATE],data[TIME])
            dt_logtime = strptime(s_logtime)
            msg = json.loads(data[MSG])

            # start, end, duration
            start = strptime(msg['START'])
            end = strptime(msg['END'])
            td=end-start
            duration=int(total_seconds(td))
            msg['DURATION'] = duration

            return  msg

        raise PygsterParsingException, "Could not parse line"

class AsyncQueue(ECBasePygsterParser):
    def __init__(self, option_string=None):
        self.count = {}
        self.exec_time = {}

    def parse_line(self, line):
        try:
            msg = super(AsyncQueue, self).parse_line(line)
            server = msg['SERVERNAME']
            job = msg['JOBTYPE'].split('.')[-1]

            # add one to number of executions of job
            try:
                self.count[job] += 1
            except KeyError:
                self.count[job] = 1

            # record execution time of job
            try:
                self.exec_time[job] += msg['DURATION']
            except KeyError:
                self.exec_time[job] = msg['DURATION']

        except Exception, e:
            raise PygsterParsingException, ""

    def get_state(self, duration):
        for job, count in self.count.iteritems():
            yield MetricObject("%s.completed" % job, count, "Jobs processed")
        for job, exec_time in self.exec_time.iteritems():
            yield MetricObject("%s.total_exec_time" % job, exec_time, "Total job execution time in seconds")

class BillRun(ECBasePygsterParser):
    def __init__(self, option_string=None):
        self.count = 0
        self.exec_time = 0
        self.query_exec_time = {}

    def parse_line(self, line):
        try:
            msg = super(BillRun, self).parse_line(line)
            self.count += 1
            self.exec_time += msg['DURATION']

            for key, value in msg.iteritems():
                k = key.lower()
                if k.startswith('query_'):
                    v = int(value) / 1000.0
                    try:
                        self.query_exec_time[k] += v
                    except KeyError:
                        self.query_exec_time[k] = v

        except PygsterParsingException:
            raise
        except Exception, e:
            raise PygsterParsingException, ""

    def get_state(self, duration):
        yield MetricObject("completed", self.count, "Jobs completeted")
        yield MetricObject("total_exec_time", self.exec_time, "Total job execution time in seconds")

        for query, exec_time in self.query_exec_time.iteritems():
            yield MetricObject("%s_total_exec_time" % query, exec_time, "Total query execution time in milliseconds")

