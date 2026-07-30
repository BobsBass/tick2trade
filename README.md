# tick2trade

[![CI](https://github.com/<your-github-username>/tick2trade/actions/workflows/ci.yml/badge.svg)](https://github.com/<your-github-username>/tick2trade/actions/workflows/ci.yml)

**A line-rate NASDAQ TotalView-ITCH 5.0 market-data feed handler, hardware limit order book, and sub-microsecond trigger-to-order path on a Zynq UltraScale+ ZCU102 — verified against a full real trading day with cocotb + Verilator, with Linux userspace control software on the PS.**

🚧 Building in public. **v1.0 target: Aug 15, 2026.**

---

## Why

Exchange market data arrives as an unthrottled firehose. A software feed handler buffers, queues, and jitters; an FPGA feed handler consumes it at wire rate with deterministic, cycle-countable latency. This project builds that path end to end — Ethernet → MoldUDP64 → ITCH decode → order book → trigger → order egress — and proves it against a real Nasdaq trading day rather than synthetic stimulus.

**The design contract: never throttle, never backpressure the feed.** On overflow the design drops and counts, like the real thing.

## Architecture

```
                    ┌─────────────────────────────────────────── PL (FPGA fabric) ──┐
 10G Ethernet       │  ┌──────────┐   ┌──────────┐   ┌───────────┐   ┌───────────┐  │
 (XXV/10G MAC, ───► │  │ UDP/     │──►│ MoldUDP64│──►│ ITCH 5.0  │──►│  Order    │  │
  SFP+ loopback     │  │ Eth RX   │   │ framer   │   │ decoder   │   │  Book     │  │
  or PS injection)  │  │ parser   │   └──────────┘   └───────────┘   │  Engine   │  │
                    │  └──────────┘        AXI-Stream 64b @ 156.25   └─────┬─────┘  │
                    │                                                      ▼        │
                    │  ┌──────────┐   ┌───────────────┐   ┌────────────────────┐    │
 10G TX  ◄───────── │  │ UDP TX   │◄──│ Order egress  │◄──│ Trigger engine     │    │
                    │  │ encap    │   │ (OUCH-style   │   │ (threshold cross → │    │
                    │  └──────────┘   │  template)    │   │  fire), latency    │    │
                    │                 └───────────────┘   │  counters          │    │
                    │        AXI4-Lite CSRs  ▲            └────────────────────┘    │
                    └────────────────────────┼──────────────────────────────────────┘
                                             │
                    ┌── PS (Cortex-A53, Linux) ─────────────┐
                    │  C++ stats/control tool (uio driver), │
                    │  pcap replay injector, Python tooling │
                    └───────────────────────────────────────┘
```

**Datapath:** AXI-Stream, 64-bit @ 156.25 MHz (the standard 10G point on Xilinx IP).
**Target:** ZCU102 (XCZU9EG-2FFVB1156E).

## Status

| Module | State |
|---|---|
| Python golden model (reader / decoder / book) | 🔴 not started |
| `mold_framer` — MoldUDP64 session + sequence framing | 🔴 not started |
| `itch_decoder` — A/F/E/C/X/D/U/P field extraction | 🔴 not started |
| `order_book` — direct-mapped symbol table, top-of-book | 🔴 not started |
| `trigger_engine` + `order_egress` | 🔴 not started |
| ZCU102 integration (10G subsystem, AXI-Lite CSRs, PS tool) | 🔴 not started |

🔴 not started · 🟡 in progress · 🟢 verified

## Headline numbers

*Filled in as they are measured — every number here is measured, never estimated.*

| Metric | Value |
|---|---|
| Sustained throughput (msgs/µs, densest burst of sample day) | — |
| Wire-to-book latency | — cycles / — ns |
| Wire-to-order (tick-to-trade) latency | — cycles / — ns |
| Messages replayed vs golden model / mismatches | — / — |
| Timing closure WNS @ 156.25 MHz | — ns |
| LUT / FF / BRAM utilization | — |

## Repo layout

```
rtl/           SystemVerilog design sources
tb/            testbenches
  python/      Python golden model (reader, decoder, reference book)
  tests/       cocotb tests + Makefile
sw/            PS-side C++ control/stats tool (uio), pcap injector
constraints/   XDC timing + pin constraints
scripts/       build, replay, and CI helper scripts
docs/          spec notes, latency report, design docs
  specs/       ITCH 5.0 / MoldUDP64 / OUCH PDFs (not committed)
```

## Build & test

```bash
# simulation regression (Verilator + cocotb)
make -C tb/tests sim

# lint + tests, exactly as CI runs them
./scripts/ci_check.sh
```

## Verification approach

Every RTL module is checked against the Python golden model in lockstep on **real** Nasdaq ITCH sample-day data, not synthetic stimulus. The regression runs on every push via GitHub Actions. SystemVerilog assertions live in the design; functional coverage tracks message types and edge cases (length fields straddling beat boundaries, sequence gaps, book-crossing conditions).

## References

Specs from [nasdaqtrader.com](https://www.nasdaqtrader.com/); sample trading days from Nasdaq's public [ITCH archive](https://emi.nasdaq.com/ITCH/Nasdaq%20ITCH/). Open-source Ethernet/NIC work by Alex Forencich (`verilog-ethernet`, `corundum`) was read as reference material; all RTL here is written from scratch.

## License

MIT — see [LICENSE](LICENSE).
