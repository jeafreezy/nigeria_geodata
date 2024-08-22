import time
import asyncio
from nigeria_geodata.datasources import Grid3
from nigeria_geodata.datasources import AsyncGrid3


# the healthcare data has over 40k rows
# so testing it with it will give an idea of the performance in a realworld usecase
def benchmark_sync():
    grid3 = Grid3()
    start_time = time.time()
    grid3.filter(
        "NGA_HealthFacilities_v1_72",
        "abuja",
    )
    elapsed_time = time.time() - start_time
    print(f"Synchronous call took {elapsed_time:.2f} seconds")


async def benchmark_async():
    grid3 = AsyncGrid3()
    start_time = time.time()
    await grid3.filter("NGA_HealthFacilities_v1_72", "abuja")
    elapsed_time = time.time() - start_time
    print(f"Asynchronous call took {elapsed_time:.2f} seconds")


def run_benchmarks():
    print("Starting synchronous benchmark...")
    benchmark_sync()

    print("Starting asynchronous benchmark...")
    asyncio.run(benchmark_async())


if __name__ == "__main__":
    run_benchmarks()
    # sync took 4.58 seconds
    # async took 0.98 seconds
    # machine - MBP 16inch. M3, 36 GB RAM.
