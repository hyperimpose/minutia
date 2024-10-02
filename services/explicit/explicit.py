from contextlib import redirect_stdout
from pathlib import Path
from typing import BinaryIO
import logging
import os
import subprocess
import tempfile

import numpy as np
import opennsfw2 as n2
from PIL import Image


logger = logging.getLogger(__name__)


try:
    a = subprocess.run(["ffmpeg", "-version"], capture_output=True)
    b = subprocess.run(["ffprobe", "-version"], capture_output=True)
    _has_ffmpeg = (a.returncode == 0) and (b.returncode == 0)
except FileNotFoundError:
    _has_ffmpeg = False
finally:
    if not _has_ffmpeg:
        logger.warning("[minutia/explicit] ffmpeg: unavailable")


model = n2.make_open_nsfw_model()


def predict_image(fp: str | Path | BinaryIO) -> float:
    pil_image = Image.open(fp)
    image = n2.preprocess_image(pil_image, n2.Preprocessing.YAHOO)
    inputs = np.expand_dims(image, axis=0)

    with open(os.devnull, 'w') as fnull:
        with redirect_stdout(fnull):
            predictions = model.predict(inputs)

    _sfw_probability, nsfw_probability = predictions[0]
    return nsfw_probability.item()


def predict_video(inpath: str | Path, duration=0) -> float:
    if not _has_ffmpeg:
        logger.warning("ffmpeg: unavailable. Returning 0.0")
        return 0.0

    if not duration:
        duration = _video_duration(inpath)

    times = [  # duration is in milliseconds
        duration / 1000 * 0.25,
        duration / 1000 * 0.50,
        duration / 1000 * 0.75
    ]
    acc = [0.0]

    # We need to add a suffix so that FFmpeg knows what format to output
    with tempfile.NamedTemporaryFile(suffix=".png") as outfp:
        for time in times:
            if _video_frame(inpath, outfp.name, time):
                return max(acc)
            acc.append(predict_image(outfp.name))

    return max(acc)


def _video_duration(path: str | Path) -> float:
    r = subprocess.run(
        ["ffprobe",
         "-v", "error",
         "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1",
         path],
        capture_output=True,
        text=True
    )
    return float(r.stdout.strip())


def _video_frame(inp: str, outp: str, at: int | float) -> int:
    r = subprocess.run(
        ["ffmpeg",
         "-y",  # automatically overwrite output
         "-hide_banner", "-loglevel", "warning",
         "-ss", str(at),  # -ss before the input is faster
         "-i", inp,
         "-frames:v", "1",
         "-update", "1",  # Only one image
         outp],
        capture_output=True
    )
    return r.returncode  # non-zero means error
