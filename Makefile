ROOT_DIR := $(realpath $(dir $(realpath $(lastword $(MAKEFILE_LIST)))))

PYTHON := python3

# The project directories are according to the OTP principles
EBIN := ${ROOT_DIR}/ebin
PRIV := ${ROOT_DIR}/priv
PRIV_BIN := ${PRIV}/bin
PYTHON_SRC := ${ROOT_DIR}/python_src

# Libminutia source code
SOURCE := ${PYTHON_SRC}/libminutia
BUILD := ${PRIV_BIN}/libminutia

# Files
PY_FILES = $(shell find ${SOURCE}/ -type f -name '*.py')
BUILD_PY_FILES = $(patsubst ${SOURCE}/%.py, ${BUILD}/%.py, $(PY_FILES))


.PHONY: all clean clean_cache

all: ${BUILD_PY_FILES}


# Note: MINUTIA_ENABLE is for installing optional dependencies for libminutia.
#       It is meant to be specified from the command line or as an environment
#       variable when running make.
#       Examples: make MINUTIA_ENABLE=explicit,media
#                 MINUTIA_ENABLE=media make
ifdef MINUTIA_ENABLE
_ME = [${MINUTIA_ENABLE}]
endif

${BUILD}/%.py: ${SOURCE}/%.py | ${BUILD}
	cp -r ${SOURCE}/* $(BUILD)

${BUILD}:
	mkdir -p ${BUILD}
    # Setup venv
	cd ${BUILD} && ${PYTHON} -m venv venv
    # Copy files and install dependencies
	cp -r ${SOURCE}/* $(BUILD)
	cd $(BUILD) \
	&& . venv/bin/activate \
	&& $(PYTHON) -m pip install .${_ME} --target $(BUILD)
    # Clean up venv
	rm -r ${BUILD}/venv


clean_cache:
    # Clean Python and Mypy cache
	cd ${SOURCE} && find . -path '*/__pycache__/*' -delete
	cd ${SOURCE} && find . -type d -name '__pycache__' -empty -delete
	cd ${SOURCE} && find . -path '*/.mypy_cache/*' -delete
	cd ${SOURCE} && find . -type d -name '.mypy_cache' -empty -delete

clean: clean_cache
	rm -rf ${PRIV_BIN}
