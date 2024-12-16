# define projects folder
BASE_DIR := ./Projects
BASE_DIR_W := Projects
BASE_DIR_W_DOT := .\Projects

# find all subfolders in projects folder
PROJECTS := $(wildcard $(BASE_DIR)/*)

# Manually define Python and pip paths from the virtual environment
PYTHON := $(shell echo $(CURDIR)/venv/Scripts/python.exe | sed 's/\//\\/g')
PIP := $(shell echo $(CURDIR)/venv/Scripts/pip.exe | sed 's/\//\\/g')

# Define Python and pip paths from the virtual environment (using backslashes for PowerShell compatibility)
#PYTHON-W := $(subst /,\,$(CURDIR)/venv/Scripts/python.exe)
#PIP-W := $(subst /,\,$(CURDIR)/venv/Scripts/pip.exe)
PYTHON-W := $(subst /,\,$(CURDIR)/$(BASE_DIR_W)/$(PROJECT)/.venv/Scripts/python.exe)
PIP-W := $(subst /,\,$(CURDIR)/$(BASE_DIR_W)/$(PROJECT)/.venv/Scripts/pip.exe)

# test rule for projects (dynamically create test targets for each project)
TESTS := $(foreach project, $(PROJECTS), $(addsuffix /tests, $(project)))

.PHONY: all clean $(TESTS) pipdeptree-all pipdeptree-project pipdeptree-all-windows pipdeptree-project-windows

# execute all tests
all: $(TESTS)
	@echo "Generated test targets: $(TESTS)"
	
# rules for testing each project (supports test.sh, make test and pytest)
$(BASE_DIR)/%/tests:
	@echo "Target directory: $(@D) ..."
	@echo "Running tests for project $(@D)..."
	@if [ -f $(@D)/test.sh ]; then \
		echo "Detected test.sh in $(@D). Running it..."; \
		cd $(@D) && bash test.sh; \
	elif [ -f $(@D)/Makefile ] && grep -q "^test:" $(@D)/Makefile; then \
		echo "Detected Makefile with 'test' target in $(@D). Running 'make test'..."; \
		cd $(@D) && make test; \
	elif [ -f $(@D)/tests/test_*.py ] || [ -f $(@D)/Tests_*.py ]; then \
		echo "Detected pytest-compatible files in $(@D). Running pytest..."; \
		cd $(@D) && $(PYTHON) -m pytest; \
	else \
		echo "No recognizable test system found in $(@D). Skipping."; \
	fi
	

# Generate pipdeptree for a single project with a provided name -> WINDOWS powershell
pipdeptree-project-windows:
	@powershell -Command " \
		if (!('$(PROJECT)' -ne '')) { \
			Write-Error 'Error: You must specify the PROJECT variable, e.g., make pipdeptree-project PROJECT=MyProject'; \
			exit 1; \
		} \
		Write-Host 'Processing project: $(BASE_DIR_W_DOT)\$(PROJECT)...'; \
		if (!(Test-Path '$(BASE_DIR_W_DOT)\$(PROJECT)')) { \
			Write-Error 'Error: The specified project $(PROJECT) does not exist in $(BASE_DIR_W_DOT).'; \
			exit 1; \
		} \
		if (!(Test-Path '$(BASE_DIR_W_DOT)\$(PROJECT)\requirements.txt')) { \
			Write-Host 'No requirements.txt found. Generating it with pip list...'; \
			Set-Location '$(BASE_DIR_W_DOT)\$(PROJECT)'; \
			& '$(PIP-W)' list --format=freeze > requirements.txt; \
			Write-Host 'requirements.txt generated for $(PROJECT).'; \
		} \
		Write-Host 'Generating pip dependency tree for $(PROJECT)...'; \
		Set-Location '$(BASE_DIR_W_DOT)\$(PROJECT)'; \
		& '$(PYTHON-W)' -m pipdeptree --graph-output svg > dependencies.svg; \
		Write-Host 'Dependency tree generated for $(PROJECT) as dependencies.svg'; \
	"

# Generate pipdeptree for all projects -> WINDOWS powershell
pipdeptree-all-windows:
	@powershell -Command " \
		Get-ChildItem -Directory '$(BASE_DIR_W_DOT)' | ForEach-Object { \
			Write-Host 'Processing project: $$_...'; \
			$projectPath = $$_; \
			if (!(Test-Path \"$($projectPath.FullName)\requirements.txt\")) { \
				Write-Host 'No requirements.txt found. Generating it with pip list...'; \
				Set-Location $projectPath.FullName; \
				& '$(PIP-W)' list --format=freeze > requirements.txt; \
				Write-Host 'requirements.txt generated for $($projectPath.Name).'; \
			} \
			Write-Host 'Generating pip dependency tree for $($projectPath.Name)...'; \
			Set-Location $projectPath.FullName; \
			& '$(PYTHON-W)' -m pipdeptree --graph-output svg > dependencies.svg; \
			Write-Host 'Dependency tree generated for $($projectPath.Name) as dependencies.svg'; \
		} \
	"
	
# Generate pipdeptree for a single project with a provided name
pipdeptree-project:
	@if [ "$(PROJECT)" = "" ]; then \
		echo "Error: You must specify the PROJECT variable, e.g., make pipdeptree-project PROJECT=MyProject"; \
		exit 1; \
	fi
	@echo "Processing project: $(BASE_DIR)/$(PROJECT)..."
	@if [ ! -d $(BASE_DIR)/$(PROJECT) ]; then \
		echo "Error: The specified project $(PROJECT) does not exist in $(BASE_DIR)."; \
		exit 1; \
	fi
	@if [ ! -f $(BASE_DIR)/$(PROJECT)/requirements.txt ]; then \
		echo "No requirements.txt found. Generating it with pip list..."; \
		cd $(BASE_DIR)/$(PROJECT) && $(PIP) list --format=freeze > requirements.txt; \
		echo "requirements.txt generated for $(PROJECT)."; \
	fi
	@echo "Generating pip dependency tree for $(PROJECT)..."; \
	cd $(BASE_DIR)/$(PROJECT) && $(PYTHON) -m pipdeptree --graph-output svg > dependencies.svg; \
	echo "Dependency tree generated for $(PROJECT) as dependencies.svg";

# Generate pipdeptree for all projects
pipdeptree-all:
	@for project in $(PROJECTS); do \
		echo "Processing project $$project..."; \
		if [ ! -f $$project/requirements.txt ]; then \
			echo "No requirements.txt found in $$project. Generating it with pip list..."; \
			cd $$project && $(PIP) list --format=freeze > requirements.txt; \
			echo "requirements.txt generated for $$project."; \
		fi; \
		echo "Generating pip dependency tree for $$project..."; \
		cd $$project && $(PYTHON) -m pipdeptree --graph-output svg > dependencies.svg; \
		echo "Dependency tree generated for $$project as dependencies.svg"; \
	done

# cleanup temp files
clean:
	@echo "Cleaning up projects..."
	@for project in $(PROJECTS); do \
		echo "Cleaning $$project..."; \
		if [ -f $$project/clean.sh ]; then \
			cd $$project && bash clean.sh; \
		else \
			find $$project -type d -name "__pycache__" -exec rm -rf {} +; \
			find $$project -type f -name "*.pyc" -delete; \
		fi; \
	done

debug:
	@echo "BASE_DIR: $(BASE_DIR)"
	@echo "PROJECTS: $(PROJECTS)"
	@echo "TESTS: $(TESTS)"
