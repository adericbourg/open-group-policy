prefix=/usr
exec_prefix=$(prefix)

PYTHON_LIB=$(prefix)/lib/python2.5
INITD=/etc/init.d
SBIN=/usr/sbin
PYTHON=`which python`
PYTHON_FLAGS=-mcompileall

OGPLIB=src/lib/ogp
OGPBIN=src/bin
DAEMON_NAME=ogpdaemon
INIT_SCRIPT_NAME=$(DAEMON_NAME)
script_path=$(INITD)/$(INIT_SCRIPT_NAME)
bin_path=$(SBIN)/$(DAEMON_NAME)

all: binaries

binaries:
	$(PYTHON) $(PYTHON_FLAGS) $(OGPLIB)

install: install-libs install-daemon

install-libs:
	@if [ ! -f $(PYTHON_LIB)/ogp ]; then \
		mkdir $(PYTHON_LIB)/ogp;\
	fi
	@cd $(OGPLIB);\
	tar -cf - --exclude='.svn' * |  tar --no-same-owner -xf - -C $(PYTHON_LIB)/ogp

install-daemon: install-daemon-bin install-daemon-initd

install-daemon-initd:
	@echo "Installing init.d script ($(script_path))..."
	@cp -f $(OGPBIN)/init.d_daemon $(script_path)
	@chmod 755 $(script_path)
	@chown 0:0 $(script_path)

install-daemon-bin:
	@echo "Installing daemon ($(bin_path))..."
	@cp -f $(OGPBIN)/$(DAEMON_NAME) $(bin_path)
	@chmod 755 $(bin_path)
	@chown 0:0 $(bin_path)

.PHONY: config clean mrproper

config:


clean:
	@echo "Removing .pyc files"
	@find $(OGPLIB) -name '*.pyc' -exec rm -v '{}' \; -print

mrproper: clean
