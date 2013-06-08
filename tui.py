import subprocess

WHIPTAIL = "/usr/bin/whiptail"

def yesno(question):
	cmd = [ WHIPTAIL, "--yesno", question, "10", str(len(question)) ]
	code = subprocess.call(cmd)
	if code == 0:
		return True
	return False

def choose(question, options):
	cmd = [ WHIPTAIL, "--menu", question, "10", "50", str(len(options)) ]
	for option in options:
		cmd.append(option[0])
		cmd.append(option[1])
	x = subprocess.Popen(cmd, stderr = subprocess.PIPE)
	y = x.communicate()
	return str(y[1])

def text(question, default):
	cmd = [ WHIPTAIL, "--inputbox", question, "8", "50", default ]
	x = subprocess.Popen(cmd, stderr = subprocess.PIPE)
	y = x.communicate()
	return str(y[1])

	
