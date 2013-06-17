#!/usr/bin/env python

import subprocess, sys

def create():
	if subprocess.call(["/usr/bin/xe-create-templates"]) <> 0:
		print >>sys.stderr, "Failed to generate templates"

if __name__ == "__main__":
	create()
