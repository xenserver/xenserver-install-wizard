.PHONY: install

DESTDIR?=/
DIR?=/usr/share/xenserver-install-wizard

install:
	mkdir -p $(DESTDIR)/$(DIR)
	install -m 0644 \
		errata.py \
		grub2.py \
		grub.py \
		hostname.py \
		interfaces.py \
		iptables.py \
		logging.py \
		network.py \
		networkscripts.py \
		openstack.py \
		replace.py \
		storage.py \
		templates.py \
		toolstack.py \
		tui.py \
		xapi.py \
		$(DESTDIR)/$(DIR)
	install -m 0755 xenserver-install-wizard.py $(DESTDIR)/$(DIR)

