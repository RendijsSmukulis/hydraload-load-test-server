from threading import Lock


class TaggedCounter(object):
    def __init__(self, counter_name, tag_name):
        self.lock = Lock()
        self.name = counter_name
        self.tag_name = tag_name
        self._counters = {}

    def inc(self, tag_key, val=1):
        """increment counter by val (default is 1)"""
        with self.lock:
            if tag_key not in self._counters:
                self._counters[tag_key] = val
            else:
                self._counters[tag_key] += val

    def dec(self, tag_key, val=1):
        """"decrement counter by val (default is 1)"""
        self.inc(tag_key, -val)

    def get_count(self, tag_key):
        """return current value of counter"""
        if tag_key not in self._counters:
            return 0

        return self._counters[tag_key]

    def get_counter_tag_keys(self):
        return self._counters.keys()

    def clear(self):
        """reset counters to 0"""
        with self.lock:
            self._counters = {}
