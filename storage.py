#!/usr/bin/env python

import sys, subprocess
import xapi

def mkdir(path):
	x = subprocess.call(["/bin/mkdir", "-p", path])
	if x <> 0:
		print >>sys.stderr, "ERROR: failed to mkdir -p %s" % path

def list_vgs():
	x = subprocess.Popen(["/sbin/vgs", "-o", "vg_name", "--noheadings"], stdout = subprocess.PIPE)
        y = x.communicate()
        ret = x.wait ()
        if ret <> 0:
		print >>sys.stderr, "ERROR: vgs failed; assuming no LVM setup"
		return []
	all = []
	for vg in y[0].split():
		vg = vg.strip()
		if vg <> "":
			all.append(vg)
	return all

def create_default_sr(tui, x, host):
	vgs = list_vgs()
	path = "/usr/share/xapi/images"
	choices = []
	choices.append((path, "Local filesystem",))
	for vg in vgs:
		choices.append((vg, "LVM Volume Group",))
	# NB we prefer LVM if available because this doesn't depend on blktap
	choice = tui.choose("Where would you like to store disk images?", choices, choices[0][0])
	if choice == "":
		return None
	if choice == path:
		mkdir(path)
		sr = x.xenapi.SR.create(host, { "path": path }, "0", path, "Files stored in %s" % path, "ffs", "default", False)
		return sr
	else:
		sr = x.xenapi.SR.create(host, { "uri": "vg:///" + choice }, "0", "Local LVM", "LVs stored in %s" % choice, "ezlvm", "default", False)
		return sr

def analyse(tui):
	x = xapi.connect()
	x.login_with_password("root", "")
	try:
		pool = x.xenapi.pool.get_all()[0]
		pool_r = x.xenapi.pool.get_record(pool)
		default_sr = pool_r["default_SR"]
		hosts = x.xenapi.host.get_all()
		
		# Set iSCSI IQN
		if not x.xenapi.host.get_other_config(hosts[0]).has_key("iscsi_iqn"):
			x.xenapi.host.add_to_other_config(hosts[0], "iscsi_iqn",
				"iqn.2013-12.com.xendomain.xenserver")

		try:
			sr_r = x.xenapi.SR.get_record(default_sr)
			print >>sys.stderr, "OK: default SR is set"
		except:
			if len(hosts) <> 1:
				print >>sys.stderr, "ERROR: host is already in a pool"
				return
			sr = create_default_sr(tui, x, hosts[0])
			if sr is None:
				return
			x.xenapi.pool.set_default_SR(pool, sr)
			x.xenapi.pool.set_suspend_image_SR(pool, sr)
			x.xenapi.pool.set_crash_dump_SR(pool, sr)
			print >>sys.stderr, "OK: created default SR"

	finally:
		x.logout()

if __name__ == "__main__":
	from tui import Tui
	analyse(Tui(False))
	
