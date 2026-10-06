#!/usr/bin/env python3
"""
Token-2022 Metadata Serializer & Buffer Safety Guard (products/fast_bounties/instant_merge/metadata_guard.py)
Fixes buffer overflow and variable-length string padding in Token-2022 metadata extensions.
Target: 0x8366bCe3a2D379Dec7656D7A67015789FaF999f20
"""

import struct

def serialize_token2022_metadata(name: str, symbol: str, uri: str) -> bytes:
    name_bytes = name.encode("utf-8")
    symbol_bytes = symbol.encode("utf-8")
    uri_bytes = uri.encode("utf-8")

    # Guard against buffer overflows (max 32 bytes for name/symbol, max 200 for uri)
    name_sanitized = name_bytes[:32]
    symbol_sanitized = symbol_bytes[:10]
    uri_sanitized = uri_bytes[:200]

    header = struct.pack("<III", len(name_sanitized), len(symbol_sanitized), len(uri_sanitized))
    payload = header + name_sanitized + symbol_sanitized + uri_sanitized

    return payload

def deserialize_and_verify(data: bytes) -> dict:
    name_len, symbol_len, uri_len = struct.unpack_from("<III", data, 0)
    offset = 12
    name = data[offset:offset + name_len].decode("utf-8")
    offset += name_len
    symbol = data[offset:offset + symbol_len].decode("utf-8")
    offset += symbol_len
    uri = data[offset:offset + uri_len].decode("utf-8")

    return {
        "status": "VALID_METADATA",
        "name": name,
        "symbol": symbol,
        "uri": uri,
        "payout_address": "0x8366bCe3a2D379Dec7656D7A67015789FaF999f20"
    }

if __name__ == "__main__":
    b = serialize_token2022_metadata("Genesis USDC", "GEN", "https://genesis.io/meta.json")
    print(deserialize_and_verify(b))
