PY := python
PY3 := python3

ALL := $(filter-out %.pyc, $(shell find $(PY) -type f))
DIRS := $(shell find $(PY) -type d)

PY3_ALL = $(patsubst $(PY)/%, $(PY3)/%, $(ALL))
PY3_DIRS = $(patsubst $(PY)/%, $(PY3)/%, $(DIRS))

.PHONY : all
all: $(PY3_ALL)

$(PY3)/%.py: $(PY)/%.py
	$(if $(wildcard $@),,$(warning Use make --always-make twice when converting new files))
	@echo Converting $@
	@cp $< $@
	@2to3 --no-diffs -wn $@

$(PY3)/%: $(PY)/%
	cp $< $@

$(PY3_ALL): | $(PY3_DIRS)

$(PY3_DIRS):
	mkdir -p $@

.PHONY : clean
clean:
	rm -rf $(PY3)