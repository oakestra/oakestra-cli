PIP := python3 -m pip 

DEBIAN_VERSION := $(shell if [ -f /etc/debian_version ]; then cat /etc/debian_version; fi)
UBUNTU_VERSION := $(shell if [ -f /etc/lsb-release ]; then grep -oP 'DISTRIB_RELEASE=\K[\d.]+' /etc/lsb-release; fi)

use_break_system_packages :=
ifneq ($(DEBIAN_VERSION),)
    ifeq ($(shell echo "$(DEBIAN_VERSION) 12" | awk '{print ($$1 >= $$2)}'),1)
        use_break_system_packages := --break-system-packages
    else ifeq ($(DEBIAN_VERSION),bookworm)
        use_break_system_packages := --break-system-packages
    endif
else ifneq ($(UBUNTU_VERSION),)
    ifeq ($(shell echo "$(UBUNTU_VERSION) 23.04" | awk '{print ($$1 >= $$2)}'),1)
        use_break_system_packages := --break-system-packages
    endif
endif

.PHONY: install-cli
install-cli:
	$(PIP) install -e . $(use_break_system_packages)

.PHONY: uninstall-cli
uninstall-cli:
	$(PIP) uninstall --yes $(use_break_system_packages) oak-cli
