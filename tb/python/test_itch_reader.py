import io
import struct

from itch_reader import read_stream


def _record(payload: bytes) -> bytes:
    return struct.pack(">H", len(payload)) + payload


def test_add_order_framing():
    # Hand-built ITCH 5.0 Add Order ('A'): type + locate(2) + tracking(2)
    # + timestamp(6) + order_ref(8) + side(1) + shares(4) + stock(8) + price(4) = 36 bytes
    payload = (
        b"A"
        + struct.pack(">HH", 1, 0)
        + (34_200_000_000_000).to_bytes(6, "big")   # 9:30:00 am in ns since midnight
        + struct.pack(">Q", 42)
        + b"B"
        + struct.pack(">I", 100)
        + b"AAPL    "                                # 8 bytes, space-padded
        + struct.pack(">I", 1_234_500)               # $123.4500 (4 implied decimals)
    )
    stream = io.BytesIO(_record(payload) + _record(b"X" + b"\x00" * 22))
    msgs = list(read_stream(stream))
    assert len(msgs) == 2
    assert msgs[0][0:1] == b"A" and len(msgs[0]) == 36
    assert msgs[1][0:1] == b"X"


def test_truncated_tail_stops_cleanly():
    stream = io.BytesIO(struct.pack(">H", 36) + b"A" + b"\x00" * 10)  # cut mid-message
    assert list(read_stream(stream)) == []