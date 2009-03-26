prefix=/usr
exec_prefix=$(prefix)

PYTHON_LIB=$(prefix)/lib/python2.5

PYTHON=`which python`
PYTHON_FLAGS=-mcompileall
OGPLIB=src/lib/ogp


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

install-daemon:


.PHONY: config clean mrproper

config:


clean:
	@echo "Removing .pyc files"
	@find $(OGPLIB) -name '*.pyc' -exec rm -v '{}' \; -print

mrproper: clean
