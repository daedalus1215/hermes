import re
import wave
import asyncio
from pathlib import Path
from typing import List, Union


class CombineWavFilesRepository:
    """A class to combine multiple WAV files from a directory into a single file."""

    def __init__(self):
        self._num_re = re.compile(r"(\d+)")
        self._chunk_frames = 64_000

    def _numeric_key(self, p: Path):
        """Extract first integer from filename for natural sort; fallback to name."""
        m = self._num_re.search(p.stem)
        return (int(m.group(1)) if m else float("inf"), p.stem, p.suffix)

    async def _find_wavs_sorted(self, folder: Path) -> List[Path]:
        """Find and sort WAV files in the given folder."""
        # List directory in thread pool since it's I/O bound
        files = await asyncio.to_thread(
            lambda: [
                p
                for p in folder.iterdir()
                if p.suffix.lower() == ".wav" and p.is_file()
            ]
        )
        if not files:
            raise ValueError(f"No .wav files found in {folder}")
        files.sort(key=self._numeric_key)
        return files

    def _params_compat(self, a: wave._wave_params, b: wave._wave_params) -> bool:
        """Check if two WAV files have compatible parameters."""
        return (
            a.nchannels == b.nchannels
            and a.sampwidth == b.sampwidth
            and a.framerate == b.framerate
            and a.comptype == b.comptype
            and a.compname == b.compname
        )

    async def combine_wav_files(
        self, input_dir: Union[str, Path], output_file: Union[str, Path]
    ) -> Path:
        """
        Combine all WAV files in the input directory into a single WAV file.

        Args:
            input_dir: Directory containing the WAV files to combine
            output_file: Output file path for the combined audio.

        Returns:
            Path: The path to the combined WAV file

        Raises:
            ValueError: If no WAV files are found or if WAV files are incompatible
        """
        input_dir = Path(input_dir)
        output_file = Path(output_file)

        # Get sorted wav files
        wavs = await self._find_wavs_sorted(input_dir)

        def process_wavs():
            """Synchronous function to process WAV files in thread pool."""
            # Open first as reference
            with wave.open(str(wavs[0]), "rb") as ref:
                ref_params = ref.getparams()

            # Create output with the same params
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with wave.open(str(output_file), "wb") as out:
                out.setparams(ref_params)

                for fp in wavs:
                    with wave.open(str(fp), "rb") as w:
                        if not self._params_compat(w.getparams(), ref_params):
                            raise ValueError(
                                f"Format mismatch in {fp.name}.\n"
                                f"All files must match: channels={ref_params.nchannels}, "
                                f"sampwidth={ref_params.sampwidth}, framerate={ref_params.framerate}, "
                                f"comptype={ref_params.comptype}."
                            )
                        # Stream frames in chunks
                        while True:
                            frames = w.readframes(self._chunk_frames)
                            if not frames:
                                break
                            out.writeframes(frames)
            return output_file

        # Run the wave processing in a thread pool since it's I/O bound
        return await asyncio.to_thread(process_wavs)
