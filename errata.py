#!/usr/bin/env python

import sys, subprocess, os, os.path, platform
import xapi, interfaces, networkscripts

# Workaround any known errata in the package builds. Hacks in here
# should be idempotent and removed as soon as the packages have been
# fixed properly.

def register_services(dry_run):
	# Work around missing post-run actions in the Debian/Ubuntu
	# packages. This function is idempotent.
	for service in [ "message-switch", "forkexecd", "ffs", "xcp-rrdd", "xcp-networkd", "squeezed", "xenopsd-xc", "xapi" ]:
		if dry_run:
			print >>sys.stdout, "update-rc.d %s defaults" % service 
		else:
			if subprocess.call(["update-rc.d", service, "defaults"]) <> 0:
				print >>sys.stderr, "FAILED to run: update-rc.d %s defaults" % service

def storage_plugin_directories(dry_run):
	# Work around mismatch between where xapi looks for SM plugins,
	# where the SM plugins look for themselves, and where they actually
	# are.
	if os.path.exists("/usr/lib64/xcp-sm"):
		target_of_link = None
		try:
			target_of_link = os.readlink("/usr/lib/xapi/sm")
		except:
			pass
		if target_of_link <> "/usr/lib64/xcp-sm":
			try:
				if dry_run:
					print >>sys.stdout, "rm -f /usr/lib/xapi/sm"
				else:
					os.unlink("/usr/lib/xapi/sm")
			except:
				pass
			if dry_run:
				print >>sys.stdout, "ln -s /usr/lib64/xcp-sm /usr/lib/xapi/sm"
			else:
				os.symlink("/usr/lib64/xcp-sm", "/usr/lib/xapi/sm")


debian_like = [ "ubuntu", "debian" ]
rhel_like = [ "fedora", "redhat", "centos" ]

def analyse(dry_run = False):
	dist = platform.linux_distribution(full_distribution_name=False)[0].lower()
	if dist in debian_like:
		register_services(dry_run)
	elif dist in rhel_like:
		storage_plugin_directories(dry_run)

if __name__ == "__main__":
	analyse(dry_run = True)
