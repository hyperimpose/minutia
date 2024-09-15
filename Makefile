ROOT_DIR := $(realpath $(dir $(realpath $(lastword $(MAKEFILE_LIST)))))

.PHONY: all clean

all: 

clean:
    # Clean Python and Mypy cache
	find . -path '*/__pycache__/*' -delete
	find . -type d -name '__pycache__' -empty -delete
	find . -path '*/.mypy_cache/*' -delete
	find . -type d -name '.mypy_cache' -empty -delete
