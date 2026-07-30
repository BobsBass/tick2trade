#!/usr/bin/env python3
"""Stream a raw NASDAQ TotalView-ITCH 5.0 file (emi.nasdaq.com archive format).

Format: repeated [2-byte big-endian length][payload] records.
First payload byte is the ITCH message type. No MoldUDP64 on disk.
"""
import argparse
import gzip
import struct
from collections import Counter


def read_stream(f, max_messages=None):
    """Yield raw ITCH message payloads from a length-prefixed stream."""
    n = 0
    while max_messages is None or n < max_messages:
        hdr = f.read(2)
        if len(hdr) < 2:
            break
        (length,) = struct.unpack(">H", hdr)
        payload = f.read(length)
        if len(payload) < length:
            break  # truncated tail - stop cleanly
        yield payload
        n += 1


def read_messages(path, max_messages=None):
    opener = gzip.open if str(path).endswith(".gz") else open
    with opener(path, "rb") as f:
        yield from read_stream(f, max_messages)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--max", type=int, default=5_000_000)
    args = ap.parse_args()

    hist = Counter()
    for msg in read_messages(args.path, args.max):
        hist[chr(msg[0])] += 1

    total = sum(hist.values())
    print(f"messages: {total:,}")
    for t, c in hist.most_common():
        print(f"  {t}  {c:>12,}  {100 * c / total:6.2f}%")


if __name__ == "__main__":
    main()