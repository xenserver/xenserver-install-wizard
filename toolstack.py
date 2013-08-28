#!/usr/bin/env python

etc_default_xen = "/etc/default/xen"

def load_file(filename):
	f = open(filename, "r")
	try:
		return f.readlines()
	finally:
		f.close()

def analyse(filename = etc_default_xen):
	old_contents = load_file(filename)
	new_contents = []
	update_needed = False
	for line in old_contents:
		line = line.strip()
		if line.startswith("TOOLSTACK="):
			t = line[len("TOOLSTACK="):].strip()
			if t <> "xapi":
				new_contents.append("TOOLSTACK=xapi")
				update_needed = True
			else:
				new_contents.append(line)
		else:
			new_contents.append(line)
	if update_needed:
		return ((filename, new_contents),)

if __name__ == "__main__":
	file_changes = analyse("toolstack/etc-default-xen")
	for change in file_changes:
		print "I propose changing %s to:" % change[0]
		for line in change[1]:
			print line
