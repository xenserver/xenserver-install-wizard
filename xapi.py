#!/usr/bin/env python

import time, sys
import XenAPI
from subprocess import call

def is_service_running(name):
	x = call(["/sbin/service", name, "status"])
	if x == 0:
		return True
	return False

def start_service(service):
	x = call(["/sbin/service", service, "start"])
	if x <> 0:
		print >>sys.stderr, "ERROR: failed to start %s" % service
	time.sleep(1)

def stop_service(service):
	x = call(["/sbin/service", service, "stop"])
	if x <> 0:
		print >>sys.stderr, "ERROR: failed to stop %s" % service

services = [
	"message-switch",
	"forkexecd",
	"xcp-networkd",
	"ffs",
	"xapi",
]

already_started = []
for service in services:
	if is_service_running(service):
		already_started.append(service)

def start():
	for service in services:
		if service not in already_started:
			start_service(service)

def open():
	return XenAPI.xapi_local()

