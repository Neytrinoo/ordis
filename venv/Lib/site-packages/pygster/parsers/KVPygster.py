#!/usr/bin/env python
"""KVPygster parses log files using k=v pairs.

Based off of MetricLogster.py from logster.
"""


import re
import optparse

from pygster.parsers import stats_helper

from pygster.pygster_helper import MetricObject, PygsterParser
from pygster.pygster_helper import PygsterParsingException


class KVPygster(PygsterParser):

    KV_REX =  '(?P<key>[^\s]+)=(?P<value>[0-9.]+)(?P<unit>[^\s$]*)'

    def __init__(self, option_string=None):
        """
        Initialize any data structures or variables needed for keeping track
        of the tasty bits we find in the log we are parsing.
        """

        self.kv_counts = {}
        self.kv_times = {}

        if option_string:
            options = option_string.split()
        else:
            options = []

        optparser = optparse.OptionParser()
        optparser.add_option(
            '--percentiles',
            '-p',
            dest='percentiles',
            default='90',
            help='Comma-separated list of integer '
            'percentiles to track: (default: "90")'
        )

        opts, args = optparser.parse_args(args=options)

        self.percentiles = opts.percentiles.split(',')

        self.kv_rex = re.compile(self.KV_REX)

    def parse_line(self, line):
        """
        Updates object state variables, one line at a time.

        :param line: Line to be parsed.
        :type line: str
        """

        kv_match = self.kv_rex.match(line)

        if kv_match:
            kv_dict = kv_match.groupdict()
            kv_key = kv_dict['key']
            kv_value = kv_dict['value']

            if 'time_' in kv_key:
                kv_unit = kv_dict['unit']

                if not kv_key in self.kv_times:
                    self.kv_times[kv_key] = {'unit': kv_unit, 'values': []}

                self.kv_times[kv_key]['values'].append(float(kv_value))
            else:
                if not kv_key in self.kv_counts:
                    self.kv_counts[kv_key] = 0.0

                self.kv_counts[kv_key] += float(kv_value)

    def get_state(self, duration):
        """
        Runs any calculations on collected data and returns metric objects.

        :param duration:
        :type duration:
        :returns: List of metric objects.
        :rtype: list
        """
        metrics = []

        if duration:
            for count_key in self.kv_counts:
                metrics.append(
                    MetricObject(
                        count_key,
                        self.kv_counts[count_key] / duration
                    )
                )

        for time_key in self.kv_times:
            values = self.kv_times[time_key]['values']
            unit = self.kv_times[time_key]['unit']

            metrics.append(
                MetricObject('.'.join([time_key, 'mean']),
                stats_helper.find_mean(values), unit)
            )

            metrics.append(
                MetricObject('.'.join([time_key, 'median']),
                stats_helper.find_median(values), unit)
            )

            metrics += [MetricObject('.'.join([time_key, "%sth_percentile" % percentile]), stats_helper.find_percentile(values, int(percentile)), unit) for percentile in self.percentiles]


        return metrics
