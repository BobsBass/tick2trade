# Spec Notes

Working notes on ITCH 5.0, MoldUDP64, and OUCH as they apply to this design.
Specs live in `docs/specs/` (not committed — download from nasdaqtrader.com).

---

## Supported ITCH 5.0 message set

The design decodes 10 message types. Everything else is counted and skipped.

| Type | Name | Why it's in scope |
|---|---|---|
| `S` | System Event | *(fill in: session start/end gating)* |
| `R` | Stock Directory | *(fill in: symbol → index mapping for the direct-mapped table)* |
| `A` | Add Order (no MPID) | |
| `F` | Add Order (with MPID) | |
| `E` | Order Executed | |
| `C` | Order Executed w/ Price | |
| `X` | Order Cancel | |
| `D` | Order Delete | |
| `U` | Order Replace | |
| `P` | Trade (non-cross) | |

**Semantics to get right the first time** *(fill in from spec §4.5–4.6)*:

- `U` (Replace) is delete-then-add with a **new** order reference number.
- `E`/`C` reduce the resting order's shares; a reduce to zero removes it.
- Price is a 4-byte unsigned int with **4 implied decimal places** (`1234500` = $123.4500).
- Timestamps are **48-bit** nanoseconds since midnight — not 64-bit. Classic bug source.
- Stock symbol is 8 bytes, **right-padded with spaces** (not NUL).
- All multi-byte fields are **big-endian**.

## Message-type histogram (real sample day)

Sample file: `12302019.NASDAQ_ITCH50.gz` · first 5,000,000 messages

```
  A     1,971,443   39.43%
  D     1,861,525   37.23%
  X       503,012   10.06%
  U       257,236    5.14%
  L       215,087    4.30%
  F       135,231    2.70%
  E        24,571    0.49%
  R         8,906    0.18%
  H         8,901    0.18%
  Y         8,897    0.18%
  P         5,185    0.10%
  K             3    0.00%
  S             2    0.00%
  V             1    0.00%
```

Notes:
- A+D = 77% — adds/deletes dominate; the decoder and book are optimized for these.
- E is low (0.49%) because the first 5M messages are mostly pre-market; expect the mix to shift toward E on the full-day replay.
- R count ≈ 8,906 = one Stock Directory message per listed symbol.
- L/H/Y/K/V are outside the supported set → counted and skipped (~4.7%, almost all L).
## MoldUDP64 framing

*(fill in: 10-byte session, 8-byte sequence number, 2-byte message count, then
length-prefixed message blocks. Note heartbeat (count=0) and end-of-session
(count=0xFFFF) cases — both are testbench edge cases.)*

## File format vs wire format

The `emi.nasdaq.com` archive files are **not** MoldUDP64 — they are a bare stream
of `[2-byte big-endian length][payload]` records. MoldUDP64 wrapping is synthesized
in the testbench with scapy so the RTL sees wire-realistic packets.

## Vivado IP license status (recorded during Week-1 power block)

| IP | License | Notes |
|---|---|---|
| 10G/25G Ethernet Subsystem | *(Included / Purchase / Eval)* | |
| AXI DMA | *(Included / Purchase / Eval)* | |
| AXI4-Stream Data FIFO | | |
| ILA / VIO | | |

## Open questions

- [ ]
