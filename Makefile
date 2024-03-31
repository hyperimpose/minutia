ROOT_DIR := $(realpath $(dir $(realpath $(lastword $(MAKEFILE_LIST)))))

ERL := erl
PYTHON := python3

# The project directories are according to the OTP principles
EBIN := ${ROOT_DIR}/ebin
SRC := ${ROOT_DIR}/src
PRIV := ${ROOT_DIR}/priv
PRIV_BIN := ${PRIV}/bin
PYTHON_SRC := ${ROOT_DIR}/python_src

# OTP Application - Rememeber to bump the version for new releases
APP_NAME := $(notdir $(ROOT_DIR))
APP_VER := 0.0.1

APP_SPEC_SRC := $(SRC)/$(APP_NAME).app.src
APP_SPEC := $(EBIN)/$(APP_NAME).app

# Libminutia source code
LIBMINUTIA := ${PYTHON_SRC}/libminutia
LIBMINUTIA_BUILD := ${PRIV_BIN}/libminutia

# Dev recipe
DEV_DEPENDS := ${ROOT_DIR}/dependencies


.PHONY: all clean dependencies dev minutia libminutia


all: libminutia minutia


dev: libminutia minutia dependencies
	erl -pz ebin ${DEV_DEPENDS}/miscellany/ebin           \
	    -eval 'logger:set_primary_config(level, debug).'  \
        -eval 'application:start(bencode).'               \
        -eval 'application:start(polycache).'             \
        -eval 'application:start(minutia).'


dependencies:
	$(info [Build] Building Erlang dependencies)
	mkdir -p ${DEV_DEPENDS}                                     \
    && rm -rf ${DEV_DEPENDS}/*                                  \
	&& cd ${DEV_DEPENDS}                                        \
	&& git clone https://github.com/hyperimpose/miscellany.git  \
	&& cd miscellany                                            \
    && make SELECT=bencode,polycache


minutia: $(APP_SPEC) | ${EBIN}
	$(info [Build] Erlang application)
	cd ${ROOT_DIR} && erl -make


${APP_SPEC}: ${APP_SPEC_SRC} | $(EBIN)
	sed 's/=version=/${APP_VER}/g' ${APP_SPEC_SRC} > ${APP_SPEC}


# Note: LM_WITH is for installing optional dependencies for libminutia.
#       It is meant to be specified from the command line when running make.
#       Examples: make LM_WITH=explicit,media
#                 make LM_WITH=media
ifdef LM_WITH
_LM_WITH = [${LM_WITH}]
endif

libminutia: | $(PRIV) $(PRIV_BIN) ${LIBMINUTIA_BUILD}
	$(info [Build] Python libminutia)
    # Clean Python and Mypy cache
	cd ${LIBMINUTIA} && find . -path '*/__pycache__/*' -delete
	cd ${LIBMINUTIA} && find . -type d -name '__pycache__' -empty -delete
	cd ${LIBMINUTIA} && find . -path '*/.mypy_cache/*' -delete
	cd ${LIBMINUTIA} && find . -type d -name '.mypy_cache' -empty -delete
    # Copy files and install dependencies
	cp -r ${LIBMINUTIA}/* $(LIBMINUTIA_BUILD)
	cd $(LIBMINUTIA_BUILD) \
	&& . venv/bin/activate \
	&& $(PYTHON) -m pip install .${_LM_WITH} --target $(LIBMINUTIA_BUILD)

${LIBMINUTIA_BUILD}: | $(PRIV) $(PRIV_BIN)
	mkdir -p ${LIBMINUTIA_BUILD}
	cd $(LIBMINUTIA_BUILD) && $(PYTHON) -m venv venv


$(EBIN) $(PRIV) $(PRIV_BIN):
	mkdir -p $@


clean:
	rm -rf $(EBIN) $(LIBMINUTIA_BUILD) ${DEV_DEPENDS}
