#!/usr/bin/env python

import grub, networking, iptables, storage

def replace_file(name, lines):
	print "Create a backup of %s" % name
	print "Replace %s with:" % name
	for line in lines:
		print line

if __name__ == "__main__":
	r = grub.analyse()
	if r:
		replace_file(r[0], r[1])
	r = networking.analyse()
	if r:
		for change in r:
			replace_file(change[0], change[1])
	r = iptables.analyse()
	if r:
		replace_file(r[0], r[1])
	storage.analyse()
	print "Welcome to XenServer!"
	
