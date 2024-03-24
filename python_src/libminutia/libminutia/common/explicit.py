from pathlib import Path
from typing import BinaryIO

try:
    import numpy as np
    import opennsfw2 as n2
    from PIL import Image
except ImportError:
    _has_explicit = False
    import warnings
    warnings.warn("[optional:explicit] unavailable", ImportWarning)
else:
    _has_explicit = True


if _has_explicit:
    model = n2.make_open_nsfw_model()


def predict_image(fp: str | Path | BinaryIO) -> float:
    if not _has_explicit:
        return 0.0

    pil_image = Image.open(fp)
    image = n2.preprocess_image(pil_image, n2.Preprocessing.YAHOO)
    inputs = np.expand_dims(image, axis=0)
    predictions = model.predict(inputs)
    _sfw_probability, nsfw_probability = predictions[0]

    return nsfw_probability
