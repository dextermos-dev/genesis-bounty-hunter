#!/usr/bin/env python3
"""MCB-01 deterministic pre-gate verifier (zero-LLM, stdlib + ffprobe).

Screens out corrupt URLs, duplicate-frame slop, wrong aspect ratios, and static
single-image fake videos before Elo / VLOOP / SOL human-finalist review.
"""
from __future__ import annotations
import hashlib, json, subprocess, sys
from pathlib import Path

REQUIRED_SHOTS = ("shot_01", "shot_02", "shot_03", "shot_04")


def probe_media(path: Path) -> dict:
    cmd = [
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=codec_name,width,height,nb_frames,r_frame_rate,duration:format=duration,size",
        "-of", "json", str(path),
    ]
    raw = subprocess.check_output(cmd, text=True, timeout=15)
    info = json.loads(raw)
    st = (info.get("streams") or [{}])[0]
    fmt = info.get("format") or {}
    w, h = int(st.get("width", 0)), int(st.get("height", 0))
    dur = float(st.get("duration") or fmt.get("duration") or 0.0)
    return {"codec": st.get("codec_name"), "width": w, "height": h, "duration": dur, "bytes": int(fmt.get("size", 0))}


def frame_motion_delta(path: Path) -> float:
    """Sample early/mid/late raw grayscale thumbnails via ffmpeg and measure L1 pixel delta."""
    frames = []
    for ss in ("0.3", "1.5", "2.7"):
        cmd = [
            "ffmpeg", "-v", "error", "-ss", ss, "-i", str(path),
            "-frames:v", "1", "-vf", "scale=64:36,format=gray", "-f", "rawvideo", "pipe:1",
        ]
        buf = subprocess.check_output(cmd, timeout=15)
        if len(buf) == 64 * 36:
            frames.append(buf)
    if len(frames) < 2:
        return 0.0
    diffs = []
    for a, b in zip(frames, frames[1:]):
        diffs.append(sum(abs(x - y) for x, y in zip(a, b)) / len(a))
    return sum(diffs) / len(diffs)


def verify_manifest(manifest_path: Path, base_dir: Path) -> int:
    doc = json.loads(manifest_path.read_text(encoding="utf-8"))
    tier = doc.get("tier", "A")
    shots = doc.get("shots") or {}
    seen_hashes = set()
    for sid in REQUIRED_SHOTS:
        if sid not in shots:
            print(f"FAIL\t{sid}\tmissing_shot")
            return 1
        entry = shots[sid]
        local_file = base_dir / entry["file"]
        if not local_file.is_file():
            print(f"FAIL\t{sid}\tmissing_file:{local_file.name}")
            return 1
        digest = hashlib.sha256(local_file.read_bytes()).hexdigest()
        if entry.get("sha256") and entry["sha256"].lower() != digest:
            print(f"FAIL\t{sid}\tsha256_mismatch")
            return 1
        if digest in seen_hashes:
            print(f"FAIL\t{sid}\tduplicate_asset_slop")
            return 1
        seen_hashes.add(digest)
        meta = probe_media(local_file)
        if meta["width"] < 960 or meta["height"] < 540:
            print(f"FAIL\t{sid}\tlow_res:{meta['width']}x{meta['height']}")
            return 1
        ratio = meta["width"] / max(meta["height"], 1)
        if not (1.65 <= ratio <= 1.85):
            print(f"FAIL\t{sid}\tbad_aspect:{ratio:.3f}")
            return 1
        if tier == "B":
            if meta["duration"] < 2.8 or meta["duration"] > 6.5:
                print(f"FAIL\t{sid}\tbad_duration:{meta['duration']:.2f}s")
                return 1
            delta = frame_motion_delta(local_file)
            if delta < 3.5:
                print(f"FAIL\t{sid}\tstatic_slideshow_slop:delta={delta:.2f}")
                return 1
    print(f"PASS\ttier={tier}\tshots=4\tunique_hashes=4")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 verify_mcb01.py <manifest.json> [asset_dir]")
        sys.exit(2)
    mp = Path(sys.argv[1])
    bd = Path(sys.argv[2]) if len(sys.argv) > 2 else mp.parent
    sys.exit(verify_manifest(mp, bd))
