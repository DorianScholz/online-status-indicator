import platform, subprocess, re

def ping(hostname, timeout):
    command = 'ping -w %s -c 1 %s' % (timeout, hostname)
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = process.stdout.read()
    matches = re.match('.*time=([0-9]+)(\.[0-9]+)?\s?ms.*', output, re.DOTALL)
    if matches:
        return int(matches.group(1))
    else: 
        return None
