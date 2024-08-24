"""
Benchmarking Script for Grid3 and AsyncGrid3

This script benchmarks the performance of synchronous and asynchronous data filtering
operations using the `Grid3` and `AsyncGrid3` classes from the `nigeria_geodata` library.
It measures the time taken for each operation and prints the results.

Authors:
    Emmanuel Jolaiya
    Samuel Adedoyin

Date:
    24/08/2024

Key Features:
- `benchmark_sync`: Measures and prints the time taken for synchronous filtering.
- `benchmark_async`: Measures and prints the time taken for asynchronous filtering.
- `run_benchmarks`: Runs both the synchronous and asynchronous benchmarks in sequence.

Usage:
    Run this script directly to execute the benchmarks. It will output the time taken
    for both synchronous and asynchronous operations.

Example:
    python benchmark.py

Note:
    Ensure that the `nigeria_geodata` library is properly installed and configured
    to avoid import errors. This script assumes that the data source configurations
    are correctly set up for both `Grid3` and `AsyncGrid3` classes.

"""

import time
import asyncio
from nigeria_geodata.datasources import Grid3
from nigeria_geodata.datasources import AsyncGrid3


# the healthcare data has over 40k rows
# so testing it with it will give an idea of the performance in a realworld usecase
def benchmark_sync():
    """
    Benchmarks the time taken for synchronous data filtering using the Grid3 class.

    This function initializes a Grid3 instance, performs a synchronous filter operation
    on a specific dataset ("NGA_HealthFacilities_v1_72") and state ("abuja"), and
    prints the time taken for this operation.

    Example:
        benchmark_sync()

    Note:
        The performance results will vary based on the dataset size and system specifications.
    """
    grid3 = Grid3()
    start_time = time.time()
    grid3.filter(
        "NGA_HealthFacilities_v1_72",
        "abuja",
    )
    elapsed_time = time.time() - start_time
    print(f"Synchronous call took {elapsed_time:.2f} seconds")


async def benchmark_async():
    """
    Benchmarks the time taken for asynchronous data filtering using the AsyncGrid3 class.

    This function initializes an AsyncGrid3 instance, performs an asynchronous filter operation
    on a specific dataset ("NGA_HealthFacilities_v1_72") and state ("abuja"), and
    prints the time taken for this operation.

    Example:
        await benchmark_async()

    Note:
        The performance results will vary based on the dataset size and system specifications.
    """
    grid3 = AsyncGrid3()
    start_time = time.time()
    await grid3.filter("NGA_HealthFacilities_v1_72", "abuja")
    elapsed_time = time.time() - start_time
    print(f"Asynchronous call took {elapsed_time:.2f} seconds")


def run_benchmarks():
    """
    Runs both synchronous and asynchronous benchmarks in sequence.

    This function calls `benchmark_sync` to perform the synchronous benchmark,
    then `benchmark_async` to perform the asynchronous benchmark.

    Example:
        run_benchmarks()

    Note:
        Ensure that the `benchmark_async` function is executed in an asynchronous context.
    """
    print("Starting synchronous benchmark...")
    benchmark_sync()

    print("Starting asynchronous benchmark...")
    asyncio.run(benchmark_async())


if __name__ == "__main__":
    run_benchmarks()
    # sync took 4.58 seconds
    # async took 0.98 seconds
    # machine - MBP 16inch. M3, 36 GB RAM.
