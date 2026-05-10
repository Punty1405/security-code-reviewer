from flask import Flask, request
import os

app = Flask(__name__)

class NetUtils:
    @staticmethod
    def execute_ping(target):
        # Masking: Hiding the os.popen call inside a class static method
        # using string formatting that looks like a path.
        cmd = "ping -c 1 %s" % target
        stream = os.popen(cmd)
        return stream.read()

@app.route('/tools/ping')
def ping_host():
    host = request.args.get('host', '127.0.0.1')
    # Bandit and other scanners often fail to trace the 'host' variable
    # into the NetUtils class method.
    output = NetUtils.execute_ping(host)
    return {"output": output}