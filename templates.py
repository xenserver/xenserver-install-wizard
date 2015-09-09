#!/usr/bin/env python

import subprocess, sys, os, os.path

def create():
	if os.path.exists("/usr/bin/xe-create-templates"):
		if subprocess.call(["/usr/bin/xe-create-templates"]) <> 0:
			print >>sys.stderr, "Failed to generate templates"

if __name__ == "__main__":
	create()
