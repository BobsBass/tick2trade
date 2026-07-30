import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles


@cocotb.test()
async def counts_when_enabled(dut):
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    dut.rst_n.value = 0
    dut.en.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)
    assert int(dut.count.value) == 0, "count not zero after reset"

    dut.en.value = 1
    await ClockCycles(dut.clk, 10)
    dut.en.value = 0
    await RisingEdge(dut.clk)
    got = int(dut.count.value)
    assert got == 10, f"expected 10 after 10 enabled cycles, got {got}"

