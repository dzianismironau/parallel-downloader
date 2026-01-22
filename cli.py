import argparse
import asyncio
from pathlib import Path

from downloader import download_many


def parse_args():
    p = argparse.ArgumentParser(description="Async parallel file downloader (aiohttp + asyncio).")
    p.add_argument("--urls", required=True, help="Path to text file with URLs (one per line).")
    p.add_argument("--out", default="downloads", help="Output directory.")
    p.add_argument("--concurrency", type=int, default=8, help="Max concurrent downloads.")
    p.add_argument("--retries", type=int, default=3, help="Retries per file.")
    p.add_argument("--timeout", type=float, default=30.0, help="Per-request timeout (seconds).")
    p.add_argument("--sequential", action="store_true", help="Download sequentially (for benchmark).")
    return p.parse_args()


def read_urls(path: str) -> list[str]:
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    return [ln.strip() for ln in lines if ln.strip() and not ln.strip().startswith("#")]


def main():
    args = parse_args()
    urls = read_urls(args.urls)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    concurrency = 1 if args.sequential else args.concurrency

    stats = asyncio.run(
        download_many(
            urls=urls,
            out_dir=out_dir,
            concurrency=concurrency,
            retries=args.retries,
            timeout_s=args.timeout,
        )
    )

    ok = sum(1 for s in stats if s["ok"])
    fail = len(stats) - ok

    print("\n=== SUMMARY ===")
    print(f"Total: {len(stats)} | OK: {ok} | FAIL: {fail}")
    for s in stats:
        if not s["ok"]:
            print(f"- FAIL: {s['url']} -> {s['error']}")


if __name__ == "__main__":
    main()