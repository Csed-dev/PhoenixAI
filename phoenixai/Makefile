# define projects folder
BASE_DIR := ./Projects

# find all subfolders in projects folder
PROJECTS := $(wildcard $(BASE_DIR)/*)

# test rule for projects (dynamically create test targets for each project)
TESTS := $(foreach project, $(PROJECTS), $(addsuffix /tests, $(project)))

.PHONY: all clean $(TESTS)

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
			cd $(@D) && pytest; \
		else \
			echo "No recognizable test system found in $(@D). Skipping."; \
		fi

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