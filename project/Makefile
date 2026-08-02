# CadetX Data Quality Pipeline — task shortcuts
#
# Usage:
#   make profile     -> run Module 1 only
#   make clean       -> run Module 2 only  (needs profile first)
#   make validate    -> run Module 3 only  (needs clean first)
#   make pipeline    -> run the full M1->M2->M3 pipeline in one command
#   make test        -> run the full test suite
#   make test-cov    -> run tests with a coverage report
#   make clean-outputs -> delete generated reports (fresh-start simulation)
#   make all         -> clean-outputs + pipeline + test, in one go
#
# DATA can be overridden, e.g.:  make pipeline DATA=data/raw/other.csv

PYTHON := python3
DATA   := data/raw/broadband_customers.csv

.PHONY: profile clean validate pipeline test test-cov clean-outputs all help

help:
	@echo "Targets: profile | clean | validate | pipeline | test | test-cov | clean-outputs | all"
	@echo "Override the dataset with: make pipeline DATA=path/to/file.csv"

profile:
	$(PYTHON) modules/m1_profiling/profiling_api.py --input $(DATA) --no-figures

clean:
	$(PYTHON) modules/m2_cleaning/clean.py --input $(DATA)

validate:
	$(PYTHON) modules/m3_validation/validate.py

pipeline:
	$(PYTHON) modules/m4_pipeline/pipeline.py --input $(DATA)

test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=modules --cov-report=term-missing

clean-outputs:
	rm -f outputs/*.json data/processed/*.csv
	@echo "Cleared outputs/ and data/processed/ — next run starts from a clean state."

all: clean-outputs pipeline test
