"""
Stress test for the MCP server using asyncio to simulate concurrent requests.

This is a simple alternative to using Locust for load testing.
"""

import asyncio
import statistics
import time
from typing import List, Dict

import httpx


async def make_request(client: httpx.AsyncClient, request_id: int) -> float:
    """
    Make a request to the MCP server and return the time it took.

    Args:
        client: The HTTP client to use
        request_id: The ID of the request

    Returns:
        The time in milliseconds that the request took
    """
    start_time = time.time()

    # Create a tool request using note_to_self
    data = {
        "jsonrpc": "2.0",
        "method": "tools/execute",
        "params": {
            "name": "note_to_self",
            "arguments": {
                "prompt": f"Test request {request_id}",
                "message": f"This is a test message from request {request_id}"
            }
        },
        "id": request_id
    }

    # Send the request
    try:
        response = await client.post("/mcp", json=data, timeout=10.0)
        
        # Calculate the time taken
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000
        
        # Ensure the response is valid
        if response.status_code != 200:
            print(f"Request {request_id} failed with status {response.status_code}: {response.text}")
            
        return duration_ms
    except httpx.TimeoutException:
        print(f"Request {request_id} timed out")
        return float('inf')  # Return infinity to indicate timeout
    except Exception as e:
        print(f"Request {request_id} failed with error: {str(e)}")
        return float('inf')  # Return infinity to indicate error


async def stress_test(url: str, num_requests: int, concurrency: int) -> Dict:
    """
    Run a stress test against the MCP server.

    Args:
        url: The URL of the MCP server
        num_requests: The total number of requests to make
        concurrency: The number of concurrent requests

    Returns:
        Statistics about the test
    """
    async with httpx.AsyncClient(base_url=url) as client:
        durations: List[float] = []

        for batch_start in range(0, num_requests, concurrency):
            batch_size = min(concurrency, num_requests - batch_start)
            batch_tasks = [
                make_request(client, i)
                for i in range(batch_start, batch_start + batch_size)
            ]

            # Wait for all requests in the batch to complete
            batch_results = await asyncio.gather(*batch_tasks)
            durations.extend(batch_results)

            # Print progress
            print(f"Completed {batch_start + batch_size}/{num_requests} requests")

    # Calculate statistics
    sorted_durations = sorted(durations)
    
    # Calculate percentiles using explicit index calculation
    p95_index = int(len(sorted_durations) * 0.95)
    p99_index = int(len(sorted_durations) * 0.99)
    
    stats = {
        "min_ms": min(durations),
        "max_ms": max(durations),
        "avg_ms": statistics.mean(durations),
        "median_ms": statistics.median(durations),
        "p95_ms": sorted_durations[p95_index],  # 95th percentile
        "p99_ms": sorted_durations[p99_index],  # 99th percentile
        "num_requests": num_requests,
        "concurrency": concurrency
    }

    return stats


async def main():
    """Run the stress test."""
    # Test parameters
    url = "http://127.0.0.1:5000"
    num_requests = 100
    concurrency = 10

    print(f"Starting stress test with {num_requests} requests, {concurrency} concurrent...")
    stats = await stress_test(url, num_requests, concurrency)

    print("\nTest Results:")
    print(f"Total Requests: {stats['num_requests']}")
    print(f"Concurrency: {stats['concurrency']}")
    print(f"Min Response Time: {stats['min_ms']:.2f} ms")
    print(f"Max Response Time: {stats['max_ms']:.2f} ms")
    print(f"Average Response Time: {stats['avg_ms']:.2f} ms")
    print(f"Median Response Time: {stats['median_ms']:.2f} ms")
    print(f"95th Percentile: {stats['p95_ms']:.2f} ms")
    print(f"99th Percentile: {stats['p99_ms']:.2f} ms")

    # Check if 95th percentile is under 200ms
    if stats['p95_ms'] <= 200:
        print("\n✅ SUCCESS: 95th percentile response time is under 200ms")
    else:
        print(f"\n❌ FAIL: 95th percentile response time ({stats['p95_ms']:.2f}ms) "
              f"exceeds 200ms target")


if __name__ == "__main__":
    asyncio.run(main())

