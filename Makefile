.PHONY: install

DESTDIR?=/
DIR?=/usr/share/xenserver-install-wizard

install:
	mkdir -p $(DESTDIR)/$(DIR)
	install -m 0644 \
		grub.py \
		hostname.py \
		iptables.py \
		logging.py \
		networking.py 
		openstack.py \
		replace.py \
		storage.py 
		templates.py \
		tui.py \
		xapi.py \
		$(DESTDIR)/$(DIR)
	install -m 0755 xenserver-install-wizard.py $(DESTDIR)/$(DIR)

