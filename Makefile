# Define the virtual environment directory
VENV = .venv
# Define the python interpreter
PYTHON = $(VENV)/Scripts/python
# Define the pip executable
PIP = $(VENV)/Scripts/pip

##########################################################################################################

# Target for setting up virtual environment + installing dependencies
# note use python version 3.11
install: requirements.txt
	test -d $(VENV) || python -m venv $(VENV)
	$(PYTHON) -m pip install --upgrade pip
	$(PIP) install -r requirements.txt

##########################################################################################################
# Define the default target. When you run "make", this is what it will do.
all: run

# Target for running your script
run: install
	$(PYTHON) combine.py
	$(PYTHON) vectordb.py
	$(PYTHON) conversation.py

##########################################################################################################

clean:
	rm -rf __pycache__
	rm -rf .vscode
# this cleans in the src directory
	rm -rf src/__pycache__ 
	rm -rf $(VENV)

# Phony targets are not files
.PHONY: all run run-other install clean

# ctrl + c to end session