import argparse
import random
import sys
import threading
import time
import urllib.error
import urllib.request


ENDPOINT_WEIGHTS = [
    ("/player/login", 0.35),
    ("/game/session", 0.30),
    ("/matchmaking/find", 0.25),
    ("/health", 0.10),
]


def choose_endpoint() -> str:
    endpoints = [path for path, _ in ENDPOINT_WEIGHTS]
    weights = [weight for _, weight in ENDPOINT_WEIGHTS]
    return random.choices(endpoints, weights=weights, k=1)[0]


def worker(
    worker_id: int,
    base_url: str,
    stop_time: float,
    min_sleep: float,
    max_sleep: float,
    timeout: float,
    counters: dict,
    lock: threading.Lock,
) -> None:
    while time.time() < stop_time:
        endpoint = choose_endpoint()
        url = f"{base_url}{endpoint}"

        try:
            with urllib.request.urlopen(url, timeout=timeout) as response:
                status_code = response.getcode()
                response.read()
        except urllib.error.HTTPError as exc:
            status_code = exc.code
        except Exception:
            status_code = "error"

        with lock:
            counters["total"] += 1
            key = f"status_{status_code}"
            counters[key] = counters.get(key, 0) + 1

        time.sleep(random.uniform(min_sleep, max_sleep))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate baseline traffic for the NexaPlay FastAPI app."
    )
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="Base URL for the NexaPlay app.",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=300,
        help="How long to run in seconds. Default: 300 (5 minutes).",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Number of concurrent worker threads. Default: 4.",
    )
    parser.add_argument(
        "--min-sleep",
        type=float,
        default=0.2,
        help="Minimum pause between requests per worker in seconds.",
    )
    parser.add_argument(
        "--max-sleep",
        type=float,
        default=1.0,
        help="Maximum pause between requests per worker in seconds.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=5.0,
        help="Per-request timeout in seconds.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.duration <= 0:
        print("--duration must be greater than 0", file=sys.stderr)
        return 1

    if args.workers <= 0:
        print("--workers must be greater than 0", file=sys.stderr)
        return 1

    if args.min_sleep < 0 or args.max_sleep < 0 or args.min_sleep > args.max_sleep:
        print("--min-sleep must be >= 0 and <= --max-sleep", file=sys.stderr)
        return 1

    base_url = args.base_url.rstrip("/")
    stop_time = time.time() + args.duration
    counters = {"total": 0}
    lock = threading.Lock()

    print(
        f"Generating traffic against {base_url} for {args.duration} seconds "
        f"with {args.workers} workers..."
    )

    threads = [
        threading.Thread(
            target=worker,
            args=(
                worker_id,
                base_url,
                stop_time,
                args.min_sleep,
                args.max_sleep,
                args.timeout,
                counters,
                lock,
            ),
            daemon=True,
        )
        for worker_id in range(args.workers)
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    total = counters.get("total", 0)
    successes = sum(
        count for key, count in counters.items() if key.startswith("status_2")
    )
    server_errors = sum(
        count for key, count in counters.items() if key.startswith("status_5")
    )
    failures = counters.get("status_error", 0)

    print("Load generation complete.")
    print(f"Total requests sent: {total}")
    print(f"2xx responses: {successes}")
    print(f"5xx responses: {server_errors}")
    print(f"Transport failures: {failures}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
