import asyncio
import hashlib
import os
import random
import re
import time
from pathlib import Path
from urllib.parse import urlparse

import aiohttp
from tqdm import tqdm


FILENAME_FALLBACK = "download.bin"
CHUNK_SIZE = 1024 * 256


def safe_filename_from_url(url: str) -> str:
    parsed = urlparse(url)
    name = os.path.basename(parsed.path) or FILENAME_FALLBACK

    name = re.sub(r"[^\w\-.]+", "_", name)
    return name[:200]


def unique_path(out_dir: Path, filename: str) -> Path:
    path = out_dir / filename
    if not path.exists():
        return path

    stem = path.stem
    suffix = path.suffix
    for i in range(1, 10_000):
        candidate = out_dir / f"{stem}__{i}{suffix}"
        if not candidate.exists():
            return candidate
    raise RuntimeError("Too many filename collisions")


async def fetch_to_file(
    session: aiohttp.ClientSession,
    url: str,
    out_dir: Path,
    retries: int,
    timeout_s: float,
    pbar: tqdm,
) -> dict:
    t0 = time.perf_counter()
    last_err = None

    for attempt in range(retries + 1):
        try:
            timeout = aiohttp.ClientTimeout(total=timeout_s)
            async with session.get(url, timeout=timeout) as resp:
                resp.raise_for_status()

                filename = safe_filename_from_url(url)
                path = unique_path(out_dir, filename)

                sha256 = hashlib.sha256()
                total = resp.content_length

                with open(path, "wb") as f:
                    async for chunk in resp.content.iter_chunked(CHUNK_SIZE):
                        if not chunk:
                            continue
                        f.write(chunk)
                        sha256.update(chunk)
                        pbar.update(len(chunk))

                dt = time.perf_counter() - t0
                return {
                    "ok": True,
                    "url": url,
                    "path": str(path),
                    "bytes": path.stat().st_size,
                    "content_length": total,
                    "sha256": sha256.hexdigest(),
                    "seconds": dt,
                    "attempts": attempt + 1,
                }

        except Exception as e:
            last_err = str(e)
            if attempt < retries:
                backoff = (2 ** attempt) * 0.5 + random.random() * 0.25
                await asyncio.sleep(backoff)
            else:
                break

    dt = time.perf_counter() - t0
    return {
        "ok": False,
        "url": url,
        "error": last_err or "unknown error",
        "seconds": dt,
        "attempts": retries + 1,
    }


async def download_many(
    urls: list[str],
    out_dir: Path,
    concurrency: int = 8,
    retries: int = 3,
    timeout_s: float = 30.0,
) -> list[dict]:
    connector = aiohttp.TCPConnector(limit=concurrency, ssl=False)
    sem = asyncio.Semaphore(concurrency)

    pbar = tqdm(total=0, unit="B", unit_scale=True, desc="Downloading", dynamic_ncols=True)

    async with aiohttp.ClientSession(connector=connector) as session:

        async def bound_task(u: str):
            async with sem:
                return await fetch_to_file(session, u, out_dir, retries, timeout_s, pbar)

        tasks = [asyncio.create_task(bound_task(u)) for u in urls]
        results = await asyncio.gather(*tasks)

    pbar.close()
    return results