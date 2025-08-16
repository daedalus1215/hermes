#!/usr/bin/env python3
import argparse
import os
import re
import wave
from pathlib import Path
from typing import List

NUM_RE = re.compile(r"(\d+)")

def numeric_key(p: Path):
    # Extract first integer from filename for natural sort; fallback to name
    m = NUM_RE.search(p.stem)
    return (int(m.group(1)) if m else float("inf"), p.stem, p.suffix)

def find_wavs_sorted(folder: Path) -> List[Path]:
    files = [p for p in folder.iterdir() if p.suffix.lower() == ".wav" and p.is_file()]
    if not files:
        raise SystemExit(f"No .wav files found in {folder}")
    files.sort(key=numeric_key)
    return files

def params_compat(a: wave._wave_params, b: wave._wave_params) -> bool:
    # Ignore nframes – we’ll write and let wave set the final count
    return (
        a.nchannels == b.nchannels and
        a.sampwidth == b.sampwidth and
        a.framerate == b.framerate and
        a.comptype  == b.comptype  and
        a.compname  == b.compname
    )

def concat_wavs(input_dir: Path, output_file: Path, chunk_frames: int = 64_000):
    wavs = find_wavs_sorted(input_dir)

    # Open first as reference
    with wave.open(str(wavs[0]), "rb") as ref:
        ref_params = ref.getparams()

    # Create output with the same params
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(output_file), "wb") as out:
        out.setparams(ref_params)

        total_frames = 0
        for fp in wavs:
            with wave.open(str(fp), "rb") as w:
                if not params_compat(w.getparams(), ref_params):
                    raise SystemExit(
                        f"Format mismatch in {fp.name}.\n"
                        f"All files must match: channels={ref_params.nchannels}, "
                        f"sampwidth={ref_params.sampwidth}, framerate={ref_params.framerate}, "
                        f"comptype={ref_params.comptype}."
                    )
                # Stream frames in chunks
                while True:
                    frames = w.readframes(chunk_frames)
                    if not frames:
                        break
                    out.writeframes(frames)
                    total_frames += len(frames) // ref_params.sampwidth // ref_params.nchannels

    print(f"Wrote {output_file} from {len(wavs)} file(s).")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Concatenate WAV files seamlessly.")
    parser.add_argument("--input-dir", "-i", default="audio", type=Path,
                        help="Directory containing input .wav files (default: ./audio)")
    parser.add_argument("--output", "-o", default="combined.wav", type=Path,
                        help="Output WAV file path (default: combined.wav)")
    args = parser.parse_args()

    concat_wavs(args.input_dir, args.output)
