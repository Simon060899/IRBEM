OS?=linux64
ENV?=gfortran64

include compile/$(OS)-$(ENV).make

BIN_DIR = bin
LIB_NAME = $(BIN_DIR)/$(COMPILE_LIB_NAME)
all: compile
compile: $(LIB_NAME)

#------------------------------------------------------------------------------
# Version information
#     RELEASE : Git version description (tag if possible, else commit hash).
#     REV : Git "revision number". Will increase between releases.
#------------------------------------------------------------------------------

HAS_GIT=$(shell if [ -e .git ] ; then echo 1 ; else echo 0; fi)
ifeq ($(HAS_GIT),1)
	RELEASE ?= $(shell git describe --always)
	REV     ?= $(shell git rev-list --count --first-parent HEAD)
else
	RELEASE ?= "UNKNOWN"
	REV     ?= -1
endif
BUILD_DATE=$(shell date +%Y-%m-%dT%H:%M)

SRC_DIR = source
$(SRC_DIR)/fortran_version.inc : 
	@echo "Creating $@ for version $(REV). Set REV to override."
	@echo "        INTEGER*4 FORTRAN_VERSION ! generated by Makefile $(BUILD_DATE)" > $@
	@echo "        PARAMETER (FORTRAN_VERSION = $(REV) ) ! Generated by Makefile"  >> $@

$(SRC_DIR)/fortran_release.inc :
	@echo "Creating $@ for release $(RELEASE) Set RELEASE to override."
	@echo "        CHARACTER*80 FORTRAN_RELEASE ! Generated by Makefile  $(BUILD_DATE)" > $@
	@echo "        PARAMETER (FORTRAN_RELEASE = '$(RELEASE)')"                     >> $@

.PHONY : $(SRC_DIR)/fortran_version.inc $(SRC_DIR)/fortran_release.inc

#------------------------------------------------------------------------------
#     myOwnMagField
#     Set the MYOWNMAGFIELD_DIR parameter to directory containing the fields
#------------------------------------------------------------------------------
MYOWNMAGFIELD_DIR?=./src_desp

myOwnMagField-pre :
	@if [ -d "$(MYOWNMAGFIELD_DIR)" ] ; then \
		echo "Found magnetic field in $(MYOWNMAGFIELD_DIR) - copying"; \
		mv $(SRC_DIR)/myOwnMagField.f $(SRC_DIR)/myOwnMagField.f.default; \
		mv $(SRC_DIR)/myOwnMagField_init.f $(SRC_DIR)/myOwnMagField_init.f.default; \
		cp $(MYOWNMAGFIELD_DIR)/myOwnMagField*.f $(SRC_DIR); \
	fi

myOwnMagField-post : $(LIB_NAME)
	@if [ -d "$(MYOWNMAGFIELD_DIR)" ] ; then \
		echo "Restoring magnetic field"; \
		mv $(SRC_DIR)/myOwnMagField.f.default $(SRC_DIR)/myOwnMagField.f; \
		mv $(SRC_DIR)/myOwnMagField_init.f.default $(SRC_DIR)/myOwnMagField_init.f; \
	fi

.PHONY: myOwnMagField-pre myOwnMagField-post
compile: myOwnMagField-post
$(SRC_DIR)/myOwnMagField.f : myOwnMagField-pre
$(SRC_DIR)/myOwnMagField_init.f : myOwnMagField-pre

#------------------------------------------------------------------------------
#     Sources and compilation rules
#------------------------------------------------------------------------------


F77_SOURCES = $(wildcard $(SRC_DIR)/*.f)
C99_SOURCES = $(wildcard $(SRC_DIR)/*.c)

F77_OBJS = $(patsubst $(SRC_DIR)/%.f,$(BIN_DIR)/%.o,$(F77_SOURCES))
C99_OBJS = $(patsubst $(SRC_DIR)/%.c,$(BIN_DIR)/%.o,$(C99_SOURCES))

$(BIN_DIR)/onera_desp_lib.o : $(SRC_DIR)/fortran_version.inc $(SRC_DIR)/fortran_release.inc

$(BIN_DIR)/%.o : $(SRC_DIR)/%.f
	$(FC) $(FFLAGS) -c -o $@ $< 

$(BIN_DIR)/%.o : $(SRC_DIR)/%.c
	$(CC) $(CFLAGS) -c -o $@ $< 

$(LIB_NAME) : $(F77_OBJS) $(C99_OBJS)
	$(LD) $(LDFLAGS) -o $@ $^

#------------------------------------------------------------------------------
#     Install
#------------------------------------------------------------------------------
INSTALLDIR?=.
install : $(LIB_NAME)
	@echo Installing
	@echo Creating $(INSTALLDIR)
	@mkdir -p $(INSTALLDIR)
	@echo Installing $(LIB_NAME) to  $(INSTALLDIR)/$(INSTALL_LIB_NAME)
	@install $(LIB_NAME) $(INSTALLDIR)/$(INSTALL_LIB_NAME)
	@echo Installing done
	# @echo TOP-LEVEL IRBEM DIR: $(shell ls *.dll)  # TODO: Remove

clean:
	rm -f $(BIN_DIR)/*.o
	rm -f $(LIB_NAME)

.PHONY: clean all compile install
