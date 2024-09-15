client = None  # Externally initialized


async def predict_image(inpath: str) -> float:
    if not client:
        return 0.0

    return await client.predict_image(inpath)


async def predict_video(inpath: str, duration=0) -> float:
    if not client:
        return 0.0

    return await client.predict_video(inpath)
