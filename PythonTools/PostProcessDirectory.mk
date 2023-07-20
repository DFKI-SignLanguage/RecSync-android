ifndef RECSYNC_DOWNLOAD_DIR
$(error RECSYNC_DOWNLOAD_DIR variable is not set)
endif

# Remove trailing slash, if any
RECSYNC_DOWNLOAD_DIR := $(patsubst %/,%,$(RECSYNC_DOWNLOAD_DIR))

# E.g.: path/to/230531-ExposureTests

ALL_SESSIONS := $(wildcard $(RECSYNC_DOWNLOAD_DIR)/*)

PARENT_DIR = $(dir $(RECSYNC_DOWNLOAD_DIR))
DIR_NAME = $(notdir $(RECSYNC_DOWNLOAD_DIR))
DEST_DIR = $(PARENT_DIR)$(DIR_NAME)-postproc

# Compose the names of the target dirs
DEST_SESSIONS = $(subst $(RECSYNC_DOWNLOAD_DIR),$(DEST_DIR),$(ALL_SESSIONS))
# Append a "/_done", which will be used as destination target file
DEST_SESSIONS := $(addsuffix /_done,$(DEST_SESSIONS))

# Debugging ...
#@echo $(ALL_SESSIONS)
#@echo PARENT: $(PARENT_DIR)
#@echo DIR_NAME: $(DIR_NAME)
#@echo DEST_DIR: $(DEST_DIR)
#@echo Wanna create: $(DEST_SESSIONS)

all: $(DEST_SESSIONS)
	@echo Filled dir $(DEST_DIR)

# Rule matching the pattern in the DEST_SESSIONS items
$(DEST_DIR)/%/_done: $(RECSYNC_DOWNLOAD_DIR)/% | $(DEST_DIR)
	$(eval tgt_dir = $(dir $@))
	@echo "Processing $< into $(tgt_dir)..."
	mkdir -p "$(tgt_dir)"
	python PostProcessVideos.py -i "$<" -o "$(tgt_dir)"
	touch "$@"

$(DEST_DIR):
	mkdir -p $@
