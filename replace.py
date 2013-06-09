#!/usr/bin/env python

import os, os.path, sys, subprocess

def choose_filename(name, prefix):
	# choose a name for the backup file that doesn't exist yet
	i = 0
	stem = os.path.dirname(name) + "/" + prefix + "." + os.path.basename(name)
	filename = stem
	while os.path.exists(filename):
		filename = stem + "." + str(i)
		i = i + 1
	return filename

def cp(existing, new):
	cmd = [ "/bin/cp", "-f", existing, new ]
	x = subprocess.call(cmd)
	if x <> 0:
		print >>sys.stderr, "FAILED: to create backup file (%s)" % (" ".join(cmd))
		exit(1)

def write(filename, contents):
	f = open(filename, "w")
	try:
		for line in contents:
			f.write(line)
			f.write("\n")
	finally:
		f.close()

def file(name, contents):
	backup = choose_filename(name, "backup")
	cp(name, backup)
	print >>sys.stderr, "OK: saved backup of %s in %s" % (name, backup)
	new = choose_filename(name, "new")
	write(new, contents)
	os.rename(new, name)

		
