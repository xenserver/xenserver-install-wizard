#!/usr/bin/env python

import sys, os, os.path, tempfile

from glob import glob
import platform
import re
import shutil
import subprocess
import tempfile
import tui

GRUB_CONF = "/etc/default/grub"

editenv = "grub-editenv"
if platform.dist()[0] in ['fedora', 'redhat', 'centos']:
	editenv = "grub2-editenv"

def list_kernels_grub2():
        grub_cfg = glob("/boot/grub*/grub.cfg")[0]

	f = open(grub_cfg, "r")
	lines = f.readlines()
	f.close()

	result = []

	regex = re.compile("^menuentry '([^']+)'.*$")
	for line in lines:
		m = regex.match(line)
		if m:
			result.append(m.group(1))
	return result


def get_default(lines):
        for line in lines:
                line = line.strip()
                if line.startswith("GRUB_DEFAULT="):
                        return line[len("GRUB_DEFAULT="):].strip('"')


def analyse(filename = GRUB_CONF):

	f = open(filename, "r")
	lines = f.readlines()
	f.close()

	default_entry = get_default(lines)

	kernels = list_kernels_grub2()

	default_type = "name"
	if default_entry == "saved":
		default_type = "saved-name"
		output = subprocess.check_output([editenv, "list"]).split("\n")
		for line in output:
			if line.startswith("saved_entry="):
				default_entry=line[len("saved_entry="):]
			if default_entry.isdigit():
				default_type = "saved-digit"
				default_entry = kernels[int(default_entry)]
			break

	if default_entry.isdigit():
		default_type = "digit"
		default_entry = kernels[int(default_entry)]	

	if "xen" in default_entry.lower():
		print >>sys.stderr, "OK: default kernel is xen"
		return
 
	if not(tui.yesno("Would you like me to make xen the default in grub.conf?")):
		print >>sys.stderr, "WARNING: system is not going to boot xen by default"
		return

	xen_entry = ""
	for kernel in kernels:
		print kernel
		if kernel.startswith(default_entry) and "xen" in kernel.lower():
			if "name" in default_type:
				xen_entry = kernel
			if "digit" in default_type:
				xen_entry = kernels.index(kernel)
			break

	new_lines = []
	if "saved" in default_type:
		tmpdir = tempfile.mkdtemp()
		filename = glob("/boot/grub*/grubenv")[0]
		tmpfilename = os.path.join(tmpdir, "grubenv")
		shutil.copy( filename, tmpfilename )
		subprocess.call([editenv, tmpfilename,
                                 "set", "saved_entry=%s" % xen_entry])
		f = open(tmpfilename)
		new_lines = f.read().split("\n")
		f.close()
		shutil.rmtree(tmpdir)
		
	else:
		for line in lines:
			tmp = line.strip()
			if tmp.startswith("GRUB_DEFAULT="):
				new_lines.append("GRUB_DEFAULT='%s'\n" % xen_entry)
			else:
				new_lines.append(line[0:-1])

	return (filename, new_lines)

if __name__ == "__main__":
	filename = GRUB_CONF
	if len(sys.argv) == 2:
		filename = sys.argv[1]
	result = analyse(filename = filename)
	if result:
		print "I propose to replace %s with:" % result[0]
		print "".join(result[1])
