#!/usr/bin/env python

import sys, os, os.path, tempfile

import tui

GRUB_CONF = "/boot/grub/grub.conf"

def list_kernels(lines):
	result = []
	current = None
	params = []

	for line in lines:
		if line.startswith("title "):
			if current <> None:
				result.append((current, params,))
			current = line[len("title "):]
			params = []
		elif current <> None:
			params.append(line)
	if current <> None and params <> []:
		result.append((current, params,))

	return result

def get_kernel((name, args,)):
	for arg in args:
		arg = arg.strip()
		if arg.startswith("kernel"):
			bits = arg.split()
			kernel = bits[1]
			return kernel

def get_default(lines):
	for line in lines:
		line = line.strip()
		if line.startswith("default="):
			return int(line[len("default="):])

def is_xen(x):
	return "xen" in get_kernel(x)

def make_xen_based_on((name, args,)):
	if not(os.path.exists("/boot/xen.gz")):
		print >>sys.stderr, "/boot/xen.gz doesn't exist: is xen installed?"
		exit(1)
	args2 = [ ]
	kernel = "kernel /xen.gz dom0_mem=752M:max:2048M loglvl=all guest_loglvl=all"
	for a in args:
		a = a.strip()
		if a.startswith("kernel "):
			args2.append("\t" + kernel)
			args2.append("\tmodule " + a[len("kernel "):])
		elif a.startswith("initrd "):
			args2.append("\tmodule " + a[len("initrd "):])
		else:
			args2.append("\t" + a)
	return (("xen", args2,))

def analyse():
	filename = GRUB_CONF
	if len(sys.argv) == 2:
		filename = sys.argv[1]

	f = open(filename, "r")
	lines = f.readlines()
	f.close()

	all = list_kernels(lines)

	xen_index = []
	default_index = get_default(lines)
	for i in range(0, len(all)):
		if is_xen(all[i]):
			xen_index.append(i)	
	if default_index in xen_index:
		print >>sys.stderr, "OK: default kernel is xen"
		return
	fd, output_filename = tempfile.mkstemp(prefix="grub")
	f = os.fdopen(fd, "w")
	if xen_index == []:
		if not(tui.yesno("Would you like me to add xen to grub.conf, based on your current default kernel and make it the default?")):
			print >>sys.stderr, "WARNING: system is not going to boot xen by default"
			return
		for line in lines:
			tmp = line.strip()
			if tmp.startswith("default="):
				print >>f, "default=%d" % (len(all))
			else:
				print >>f, line,
		(name, args,) = make_xen_based_on(all[default_index])
		print >>f, "# added by the xenserver install wizard"
		print >>f, name
		for line in args:
			print >>f, line
	else:
		if not(tui.yesno("Would you like me to make xen the default in grub.conf?")):
			print >>sys.stderr, "WARNING: system is not going to boot xen by default"
			return
		for line in lines:
			tmp = line.strip()
			if tmp.startswith("default="):
				print >>f, "default=%d" % xen_index[0]
			else:
				print >>f, line,
	f.close()
	return output_filename

if __name__ == "__main__":
	new_grub_conf = analyse()
	if new_grub_conf:
		print "I propose to replace grub.conf with %s" % new_grub_conf
