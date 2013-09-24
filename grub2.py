#!/usr/bin/env python

import sys, os, os.path, tempfile

from glob import glob
import platform
import re
import shutil
import subprocess
import tempfile

GRUB_CONF = "/etc/default/grub"
GRUB_CFG_GLOB = "/boot/grub*/grub.cfg"

editenv = "grub-editenv"
if platform.dist()[0] in ['fedora', 'redhat', 'centos']:
	editenv = "grub2-editenv"

def list_kernels_grub2(grub_cfg_glob = GRUB_CFG_GLOB):
        grub_cfg = glob(grub_cfg_glob)[0]

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
                        return line[len("GRUB_DEFAULT="):].strip("'\"")


def analyse(tui, etc_default_grub = GRUB_CONF, grub_cfg_glob = GRUB_CFG_GLOB):

	f = open(etc_default_grub, "r")
	lines = f.readlines()
	f.close()

	default_entry = get_default(lines)
	print >>sys.stderr, "current GRUB_DEFAULT=%s" % default_entry

	kernels = list_kernels_grub2(grub_cfg_glob)

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

	if default_entry == "":
		default_entry = kernels[0]
 
	if not(tui.yesno("Would you like me to make xen the default in grub.conf?", True)):
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
				new_lines.append("GRUB_DEFAULT='%s'" % xen_entry)
			else:
				new_lines.append(line[0:-1])

	return (etc_default_grub, new_lines)

if __name__ == "__main__":
	from tui import Tui
	etc_default_grub = GRUB_CONF
	grub_cfg_glob = GRUB_CFG_GLOB
	if len(sys.argv) > 1:
		etc_default_grub = sys.argv[1]
	if len(sys.argv) > 2:
		grub_cfg_glob = sys.argv[2]
	result = analyse(Tui(False), etc_default_grub = etc_default_grub, grub_cfg_glob = grub_cfg_glob)
	if result:
		print "I propose to replace %s with:" % result[0]
		print "\n".join(result[1])
