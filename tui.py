from subprocess import call

WHIPTAIL = "/usr/bin/whiptail"

def yesno(question):
	cmd = [ WHIPTAIL, "--yesno", question, "10", str(len(question)) ]
	code = call(cmd)
	if code == 0:
		return True
	return False
