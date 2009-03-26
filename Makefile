prefix=/usr
exec_prefix=$(prefix)

PYTHON_LIB=$(prefix)/lib/python2.5

PYTHON=`which python`
PYTHON_FLAGS=-mcompileall
OGPLIB=src/lib/ogp


all: binaries

binaries:
	$(PYTHON) $(PYTHON_FLAGS) $(OGPLIB)

install: install-libs

install-libs:
	@cp -rf $(OGPLIB) ~/tmp

.PHONY: config clean mrproper

config:


clean:
	@echo "Removing .pyc files"
	@find $(OGPLIB) -name '*.pyc' -exec rm -v '{}' \; -print
mrproper: clean
