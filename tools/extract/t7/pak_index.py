#!/usr/bin/env python3
"""UE4 .pak index reader + entry extractor over a ReleaseFile (range reads).

Reuses the GRE lanes' proven Tekken 7 facts (tools/extract/t7/extract_pak.sh):
  - pak AES key (public community key, credit TekkenMods / Gneiss):
    ASCII "=d6nw6YY6E#tI=6li6pI5CVaBC@fy%vR" (32 bytes, AES-256).
  - the same key fixes per-asset encryption after extraction (t7_decrypt.py).

The pak footer (FPakInfo) and index live at the END of the pak, so the whole
index is reachable with range reads long before the pak's first bytes matter.
Entry payloads are then pulled individually (compressed block by block) —
the 20 GB pak is never staged locally.

Usage:
  pak_index.py footer  --repo R --release T --parts-list L
  pak_index.py list    --repo R --release T --parts-list L --out index.json
  pak_index.py find    --index index.json <substring> [<substring> ...]
  pak_index.py extract --repo R --release T --parts-list L --index index.json \
                       --name <pak path> --out FILE
"""
import hashlib
import json
import struct
import sys
import zlib

from Crypto.Cipher import AES

PAK_MAGIC = 0x5A6F12E1
# Public community key (already in this repo: tools/extract/t7/extract_pak.sh).
PAK_KEY = b"=d6nw6YY6E#tI=6li6pI5CVaBC@fy%vR"

COMPRESSION_BY_ENUM = {0: "none", 1: "zlib", 2: "gzip", 3: "custom", 4: "oodle"}


# ---------------------------------------------------------------- footer
def parse_footer(tail, file_size):
    """Find FPakInfo in the file tail. Returns dict or raises."""
    magic = struct.pack("<I", PAK_MAGIC)
    pos = tail.rfind(magic)
    if pos < 0:
        raise ValueError("pak magic not found in tail")
    base = file_size - len(tail) + pos  # absolute offset of the magic
    p = pos + 4
    version, = struct.unpack_from("<i", tail, p); p += 4
    index_offset, index_size = struct.unpack_from("<qq", tail, p); p += 16
    index_hash = tail[p:p + 20]; p += 20
    info = {
        "footer_offset": base,
        "version": version,
        "index_offset": index_offset,
        "index_size": index_size,
        "index_sha1": index_hash.hex(),
        "bytes_after_magic": len(tail) - pos,
    }
    if version >= 5:
        # FName-based compression methods: up to 5 x 32-byte names follow.
        methods = []
        for i in range(5):
            raw = tail[p:p + 32]
            if len(raw) < 32:
                break
            methods.append(raw.split(b"\x00")[0].decode("ascii", "replace"))
            p += 32
        info["compression_methods"] = methods
    return info


# ---------------------------------------------------------------- helpers
class Cursor:
    def __init__(self, buf):
        self.buf = buf
        self.pos = 0

    def take(self, n):
        if self.pos + n > len(self.buf):
            raise ValueError("overrun")
        b = self.buf[self.pos:self.pos + n]
        self.pos += n
        return b

    def i32(self):
        return struct.unpack("<i", self.take(4))[0]

    def u32(self):
        return struct.unpack("<I", self.take(4))[0]

    def i64(self):
        return struct.unpack("<q", self.take(8))[0]

    def u8(self):
        return self.take(1)[0]

    def fstring(self):
        n = self.i32()
        if n == 0:
            return ""
        if n < 0:  # UTF-16
            raw = self.take(-2 * n)
            return raw.decode("utf-16-le").rstrip("\x00")
        raw = self.take(n)
        return raw.decode("utf-8", "strict").rstrip("\x00")


def _parse_entry(cur, variant, version):
    offset = cur.i64()
    size = cur.i64()
    unc = cur.i64()
    comp = cur.i32()
    e = {"offset": offset, "size": size, "uncompressed_size": unc,
         "compression_raw": comp, "blocks": [], "encrypted": False,
         "compression_block_size": 0}
    if variant["hash"]:
        e["sha1"] = cur.take(20).hex()
    if comp != 0:
        nblocks = cur.i32()
        if nblocks < 0 or nblocks > 100000:
            raise ValueError("bad block count")
        for _ in range(nblocks):
            s = cur.i64(); en = cur.i64()
            e["blocks"].append([s, en])
    tail = variant["tail"]
    if tail == "blocksize_then_flag":
        e["compression_block_size"] = cur.u32()
        e["encrypted"] = bool(cur.u8())
    elif tail == "flag_then_blocksize":
        e["encrypted"] = bool(cur.u8())
        e["compression_block_size"] = cur.u32()
    elif tail == "flag_only":
        e["encrypted"] = bool(cur.u8())
    elif tail == "blocksize_only":
        e["compression_block_size"] = cur.u32()
    return e


def _plausible(entries, file_size):
    for e in entries:
        if e["offset"] < 0 or e["offset"] >= file_size:
            return False
        if e["size"] < 0 or e["uncompressed_size"] < 0:
            return False
        for s, en in e["blocks"]:
            if s < 0 or en <= s:
                return False
    return True


def parse_index(buf, version, file_size):
    """Parse the (decrypted) legacy FPakIndex. Auto-tries entry layout
    variants; a variant wins only if it consumes the buffer exactly
    (AES padding aside) and every entry is plausible."""
    variants = [
        {"hash": True, "tail": "blocksize_then_flag"},
        {"hash": True, "tail": "flag_then_blocksize"},
        {"hash": True, "tail": "flag_only"},
        {"hash": True, "tail": "blocksize_only"},
        {"hash": True, "tail": "none"},
        {"hash": False, "tail": "blocksize_then_flag"},
        {"hash": False, "tail": "none"},
    ]
    errors = []
    for v in variants:
        try:
            cur = Cursor(buf)
            mount = cur.fstring()
            count = cur.i32()
            if count < 0 or count > 2_000_000:
                raise ValueError("bad count")
            entries = []
            for _ in range(count):
                name = cur.fstring()
                if not name or any(ord(c) < 9 for c in name):
                    raise ValueError("bad name")
                e = _parse_entry(cur, v, version)
                e["name"] = name
                entries.append(e)
            rest = len(buf) - cur.pos
            if rest < 0 or rest > 16:  # allow AES block padding slack
                raise ValueError(f"trailing {rest} bytes")
            if not _plausible(entries, file_size):
                raise ValueError("implausible entries")
            return mount, entries, v
        except Exception as ex:  # noqa: BLE001 - variant search
            errors.append(f"{v}: {ex}")
    raise ValueError("no index layout variant validated:\n  " + "\n  ".join(errors))


def decrypt_aes(data, mode):
    n = len(data) // 16 * 16
    if mode == "ecb":
        return AES.new(PAK_KEY, AES.MODE_ECB).decrypt(data[:n]) + data[n:]
    if mode == "cbc0":
        return AES.new(PAK_KEY, AES.MODE_CBC, iv=b"\x00" * 16).decrypt(data[:n]) + data[n:]
    raise ValueError(mode)


# ---------------------------------------------------------------- pak
class Pak:
    def __init__(self, release_file):
        self.rf = release_file
        tail_len = min(512, release_file.size)
        tail = release_file.read(release_file.size - tail_len, tail_len)
        self.footer = parse_footer(tail, release_file.size)
        raw = release_file.read(self.footer["index_offset"], self.footer["index_size"])
        self.index_sha1_raw_match = hashlib.sha1(raw).hexdigest() == self.footer["index_sha1"]
        candidates = [("plain", raw)]
        if not self.index_sha1_raw_match:
            candidates += [("ecb", decrypt_aes(raw, "ecb")),
                           ("cbc0", decrypt_aes(raw, "cbc0"))]
        last_err = None
        for mode, blob in candidates:
            try:
                self.mount, self.entries, self.layout = parse_index(
                    blob, self.footer["version"], self.rf.size)
                self.index_bytes = blob
                self.index_encryption = mode
                break
            except ValueError as ex:
                last_err = ex
        else:
            raise ValueError(f"index parse failed under all candidates: {last_err}")
        self.by_name = {e["name"]: e for e in self.entries}
        methods = self.footer.get("compression_methods")
        for e in self.entries:
            raw_c = e["compression_raw"]
            if methods and 0 <= raw_c < len(methods) and methods[raw_c]:
                e["compression"] = methods[raw_c].lower()
            else:
                e["compression"] = COMPRESSION_BY_ENUM.get(raw_c, f"method{raw_c}")

    # ---- entry data -----------------------------------------------------
    def _entry_header_len(self, entry):
        """Re-parse the duplicated entry header stored at entry.offset."""
        head = self.rf.read(entry["offset"], min(512, entry["size"] + 512))
        cur = Cursor(head)
        _parse_entry(cur, self.layout, self.footer["version"])
        return cur.pos

    def extract(self, entry):
        """Return the entry's uncompressed bytes."""
        hdr = self._entry_header_len(entry)
        base = entry["offset"]
        unc = entry["uncompressed_size"]
        if entry["compression"] in ("none", "", None) or entry["compression_raw"] == 0:
            data = self.rf.read(base + hdr, entry["size"])
            if entry["encrypted"]:
                data = decrypt_aes(data, "ecb")
            return data[:unc]
        if entry["compression"] != "zlib":
            raise ValueError(f"unsupported compression {entry['compression']} for {entry['name']}")
        out = bytearray()
        # Block offsets are stored relative to the entry offset (v>=3) and the
        # first block starts right after the in-file header. Validate with the
        # zlib magic; fall back to header-relative if needed.
        for rel_start, rel_end in entry["blocks"]:
            for origin in (base, base + hdr):
                start = origin + rel_start
                blob = self.rf.read(start, rel_end - rel_start)
                try:
                    piece = self._decompress_block(blob, entry)
                    out += piece
                    break
                except Exception:
                    continue
            else:
                raise ValueError(f"block [{rel_start},{rel_end}] of {entry['name']} "
                                 "failed under both offset interpretations")
        return bytes(out[:unc])

    def _decompress_block(self, blob, entry):
        data = blob
        if entry["encrypted"]:
            data = decrypt_aes(data, "ecb")
        piece = zlib.decompress(data)
        return piece


# ---------------------------------------------------------------- CLI
def _open_pak(a):
    from release_range import GitHubReleaseParts, ReleaseFile, load_parts_list
    parts = load_parts_list(a.parts_list)
    backend = GitHubReleaseParts(a.repo, a.release)
    keep = [(n, s) for n, s in parts if n in backend.assets]
    return Pak(ReleaseFile(backend, keep))


def main(argv):
    import argparse
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("footer", "list", "extract"):
        p = sub.add_parser(name)
        p.add_argument("--repo", required=True)
        p.add_argument("--release", required=True)
        p.add_argument("--parts-list", required=True)
    sub.choices["list"].add_argument("--out", required=True)
    sub.choices["extract"].add_argument("--index")
    sub.choices["extract"].add_argument("--name", required=True)
    sub.choices["extract"].add_argument("--out", required=True)
    p = sub.add_parser("find")
    p.add_argument("--index", required=True)
    p.add_argument("terms", nargs="+")
    a = ap.parse_args(argv)

    if a.cmd == "find":
        idx = json.load(open(a.index))
        for e in idx["entries"]:
            if all(t.lower() in e["name"].lower() for t in a.terms):
                print(f"{e['name']}\toff={e['offset']} size={e['size']} "
                      f"unc={e['uncompressed_size']} comp={e['compression']} enc={e['encrypted']}")
        return 0

    pak = _open_pak(a)
    if a.cmd == "footer":
        print(json.dumps({**pak.footer, "index_encryption": pak.index_encryption,
                          "layout": pak.layout, "mount": pak.mount,
                          "entries": len(pak.entries)}, indent=1))
    elif a.cmd == "list":
        doc = {"footer": pak.footer, "index_encryption": pak.index_encryption,
               "layout": pak.layout, "mount": pak.mount, "entries": pak.entries}
        with open(a.out, "w") as f:
            json.dump(doc, f)
        print(f"wrote {len(pak.entries)} entries to {a.out}")
    elif a.cmd == "extract":
        e = pak.by_name[a.name]
        data = pak.extract(e)
        with open(a.out, "wb") as f:
            f.write(data)
        print(f"{a.name}: {len(data)} bytes (sha256 {hashlib.sha256(data).hexdigest()[:16]}...) "
              f"-> {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
