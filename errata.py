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

debian_like = [ "ubuntu", "debian" ]
rhel_like = [ "fedora", "redhat", "centos" ]

def analyse(dry_run = False):
	distribution = platform.linux_distribution()[0].lower()
	if distribution in debian_like:
		register_services(dry_run)
	elif distribution in rhel_like:
		pass

if __name__ == "__main__":
	analyse(dry_run = True)
