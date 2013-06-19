.PHONY: install

DESTDIR?=/
DIR?=/usr/share/xenserver-install-wizard

install:
	mkdir -p $(DESTDIR)/$(DIR)
	install -m 0644 replace.py xapi.py grub.py tui.py iptables.py storage.py networking.py templates.py logging.py hostname.py $(DESTDIR)/$(DIR)
	install -m 0755 xenserver-install-wizard.py $(DESTDIR)/$(DIR)

