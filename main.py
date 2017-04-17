from aiohttp import web
from pyformance import MetricsRegistry
from opentsdb_tagcounter_reporter import OpenTSDBTagReporter
from tagged_counter import TaggedCounter
import socket
import re
import os

counter = TaggedCounter("received_messages.count", "path")
registry = MetricsRegistry()

prefix = os.getenv('HYDRALOAD_LOG_PREFIX', "hydraload")
opentsdb_host = os.getenv('HYDRALOAD_OPENTSDB_HOST', "localhost:4242")
application_name = os.getenv('HYDRALOAD_OPENTSDB_APPNAME', "appname")
write_key = os.getenv('HYDRALOAD_OPENTSDB_WRITEKEY', "writekey")

reporter = OpenTSDBTagReporter(reporting_interval=1,
                               prefix=prefix,
                               url="http://{}/api/put".format(opentsdb_host),
                               application_name=application_name,
                               write_key=write_key,
                               counters=[counter],
                               tags={"host": socket.gethostname()})
reporter.start()


async def handle(request):
    method_and_path = request.method + '/' + request.match_info.get('tail', "")
    method_and_path = re.sub(r"[^a-zA-Z0-9-_/.]", "_", method_and_path)
    counter.inc(method_and_path, 1)
    return web.Response(text='aiohttp')

app = web.Application()
app.router.add_route('*', '/{tail:.*}', handle)
print("running on host {}".format(socket.gethostbyname(socket.gethostname())))
web.run_app(app, port=5858)
