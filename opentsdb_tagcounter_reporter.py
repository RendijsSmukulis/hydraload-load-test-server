# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
from pyformance.reporters.reporter import Reporter
import base64
import json

if sys.version_info[0] > 2:
    import urllib.request as urllib
    import urllib.error as urlerror
else:
    import urllib2 as urllib
    import urllib2 as urlerror


class OpenTSDBTagReporter(Reporter):
    """
    This reporter requires a tuple (application_name, write_key) to put data to opentsdb database
    """

    def __init__(self, application_name, write_key, url, counters, reporting_interval=10, clock=None, prefix="",
                 tags={}):
        super(OpenTSDBTagReporter, self).__init__(reporting_interval=reporting_interval, clock=clock)
        self.url = url
        self.counters = counters
        self.application_name = application_name
        self.write_key = write_key
        self.prefix = prefix
        self.tags = tags or {}

    def report_now(self, registry=None, timestamp=None):
        metrics = self._collect_metrics(registry or self.registry, timestamp)
        if metrics:
            try:
                request = urllib.Request(self.url,
                                         data=self._format_data_string_for_urllib(json.dumps(metrics)),
                                         headers={'content-type': "application/json"})
                authentication_data = "{0}:{1}".format(self.application_name, self.write_key)
                auth_header = base64.b64encode(bytes(authentication_data.encode("utf-8")))
                request.add_header("Authorization", "Basic {0}".format(auth_header))
                urllib.urlopen(request)
            except Exception as e:
                sys.stderr.write("{0}\n".format(e))

    def _collect_metrics(self, registry, timestamp=None):
        timestamp = timestamp or int(round(self.clock.time()))

        metrics_data = []
        for tag_counter in self.counters:
            counter_keys = tag_counter.get_counter_tag_keys()

            for key in counter_keys:
                # TODO: these dictionary copies can be cached to avoid copying every time
                tag_dict_merged = self.tags.copy()
                tag_dict_merged.update({tag_counter.tag_name: key})

                metrics_data.append({
                    'metric': "{0}.{1}".format(self.prefix, tag_counter.name),
                    'value': tag_counter.get_count(key),
                    'timestamp': timestamp,
                    'tags': tag_dict_merged
                })

        return metrics_data

    @staticmethod
    def _format_data_string_for_urllib(data):
        if sys.version_info[0] > 2:
            return data.encode("utf-8")
        return data
