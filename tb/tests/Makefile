SIM ?= verilator
TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES = $(CURDIR)/../../rtl/smoke_counter.sv
TOPLEVEL = smoke_counter
MODULE   = test_smoke_counter
EXTRA_ARGS += --trace --trace-structs

include $(shell cocotb-config --makefiles)/Makefile.sim

