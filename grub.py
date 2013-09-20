#!/usr/bin/env python

import sys, os, os.path, tempfile

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
	kernelpath = "/boot/xen.gz"
	if os.path.ismount("/boot"):
		kernelpath = "/xen.gz"
	kernel = "kernel %s dom0_mem=2048M,max:2048M loglvl=all guest_loglvl=all" % kernelpath
	for a in args:
		a = a.strip()
		if a.startswith("kernel "):
			args2.append("\t" + kernel)
			args2.append("\tmodule " + a[len("kernel "):])
		elif a.startswith("initrd "):
			args2.append("\tmodule " + a[len("initrd "):])
		else:
			args2.append("\t" + a)
	return (("title xen", args2,))

def analyse(tui, filename = GRUB_CONF):

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
	if xen_index == []:
		if not(tui.yesno("Would you like me to add xen, based on your current default kernel, to grub.conf and make it the default?", True)):
			print >>sys.stderr, "WARNING: system is not going to boot xen by default"
			return
		new_lines = []
		for line in lines:
			tmp = line.strip()
			if tmp.startswith("default="):
				new_lines.append("default=%d" % (len(all)))
			else:
				new_lines.append(line[0:-1])
		(name, args,) = make_xen_based_on(all[default_index])
		new_lines.append("# added by the xenserver install wizard")
		new_lines.append(name)
		for line in args:
			new_lines.append(line)
		return (filename, new_lines)
	else:
		if not(tui.yesno("Would you like me to make xen the default in grub.conf?", True)):
			print >>sys.stderr, "WARNING: system is not going to boot xen by default"
			return
		new_lines = []
		for line in lines:
			tmp = line.strip()
			if tmp.startswith("default="):
				new_lines.append("default=%d" % xen_index[0])
			else:
				new_lines.append(line[0:-1])
		return (filename, new_lines)

if __name__ == "__main__":
	from tui import Tui
	filename = GRUB_CONF
	if len(sys.argv) == 2:
		filename = sys.argv[1]
	result = analyse(Tui(False), filename = filename)
	if result:
		print "I propose to replace %s with:" % result[0]
		for line in result[1]:
			print line
