#!/usr/bin/env python

import sys, subprocess, platform

RSYSLOGD_CONF="/etc/rsyslog.conf"

def analyse(tui, filename=RSYSLOGD_CONF):
	f = open(filename, "r")
	lines = f.readlines()
	f.close()
	# search for "$ModLoad imuxsock"	
	# search for "$SystemLogRateLimitInterval 2"
	# search for "$SystemLogRateLimitBurst 500"
	# search for "*.debug;*.info;mail.none;authpriv.none;cron.none                /var/log/messages"
	found_imuxsock = False
	rate_limit_interval = None
	rate_limit_burst = None
	var_log_messages = None
	for line in lines:
		line = line.strip()
		if line.startswith("$ModLoad imuxsock"):
			found_imuxsock = True
		elif line.startswith("$SystemLogRateLimitInterval "):
			rate_limit_interval = line.split()[1]
		elif line.startswith("$SystemLogRateLimitBurst "):
			rate_limit_burst = line.split()[1]
		elif line.endswith("/var/log/messages"):
			var_log_messages = line.split()[0]
	rate_limiting_needed = False
	debug_needed = False
	if found_imuxsock and not rate_limit_interval and not rate_limit_burst:
		print >>sys.stderr, "logging: I recommend setting up rate-limiting"
		if tui.yesno("Would you like me to adjust log rate-limiting to improve debugability?", True):
			rate_limiting_needed = True
	if var_log_messages and ("*.debug" not in var_log_messages):
		print >>sys.stderr, "logging: I recommend enabling debug logging"
		if tui.yesno("Would you like to enable logging for debug level messages?", True):
			debug_needed = True
	if not rate_limiting_needed and not debug_needed:
		return None
	lines2 = []
	for line in lines:
		line = line.strip()
		if line.startswith("$ModLoad imuxsock"):
			lines2.append(line)
			if rate_limiting_needed:
				lines2.append("$SystemLogRateLimitInterval 2")
				lines2.append("$SystemLogRateLimitBurst 500")
		elif line.endswith("/var/log/messages"):
			if debug_needed:
				lines2.append("*.debug;" + line)
			else:
				lines2.append(line)
		else:
			lines2.append(line)
	return (filename, lines2)

def restart():
	distro = platform.linux_distribution(full_distribution_name=False)[0].lower()
	if distro in [ 'ubuntu', 'linaro' ]:
		# Work around logging bug 
		subprocess.call(["touch", "/var/log/syslog"])
		subprocess.call(["chown", "syslog.adm", "/var/log/syslog"])

	if subprocess.call(["service", "rsyslog", "restart"]) <> 0:
		print >>sys.stderr, "FAILED: to restart rsyslog"

if __name__ == "__main__":
	from tui import Tui
	filename = RSYSLOGD_CONF
	if len(sys.argv) == 2:
		filename = sys.argv[1]
	result = analyse(Tui(False), filename = filename)
	if result:
		print "I propose the file %s is changed to read:" % result[0]
		for line in result[1]:
			print line

