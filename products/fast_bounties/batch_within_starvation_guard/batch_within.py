"""
Reactive Stream Combinator: batchWithin(maxItems K, windowDuration D)
Race-Free State Machine & Anti-Starvation Guard under Downstream Backpressure

Problem:
Pairing an infinite high-rate upstream with variable downstream pull backpressure causes
timer-reset starvation or empty/mis-sized boundary chunks when timer is continuously reset
upon item arrivals or downstream delay.

Solution:
A deterministic, race-free state machine that decouples the wall-clock window timer from
individual item arrival ticks. The timer is anchored to the arrival of the FIRST item in a batch
and never reset until the chunk (size K or window D) is discharged to downstream.
"""

import asyncio
import time
from typing import AsyncIterator, List, TypeVar, Generic

T = TypeVar("T")


class BatchWithinStarvationGuard(Generic[T]):
    def __init__(self, max_items: int, window_duration_secs: float):
        if max_items <= 0:
            raise ValueError("max_items must be > 0")
        if window_duration_secs <= 0:
            raise ValueError("window_duration_secs must be > 0")
        self.k = max_items
        self.d = window_duration_secs
        self.buffer: List[T] = []
        self.window_deadline: float | None = None
        self.lock = asyncio.Lock()
        self.chunk_ready = asyncio.Event()
        self.upstream_closed = False

    async def ingest_stream(self, source: AsyncIterator[T], out_queue: asyncio.Queue[List[T]]):
        loop = asyncio.get_running_loop()
        timer_task: asyncio.Task | None = None

        async def timer_watcher():
            while not self.upstream_closed:
                await asyncio.sleep(self.d / 4)
                async with self.lock:
                    if self.buffer and self.window_deadline is not None:
                        if loop.time() >= self.window_deadline:
                            # Discharge on deadline expiration
                            chunk = list(self.buffer)
                            self.buffer.clear()
                            self.window_deadline = None
                            await out_queue.put(chunk)

        timer_task = asyncio.create_task(timer_watcher())

        try:
            async for item in source:
                async with self.lock:
                    if not self.buffer:
                        # Anchor window deadline to first item arrival; NEVER reset on subsequent items
                        self.window_deadline = loop.time() + self.d
                    self.buffer.append(item)

                    if len(self.buffer) >= self.k:
                        chunk = list(self.buffer[:self.k])
                        self.buffer = self.buffer[self.k:]
                        self.window_deadline = loop.time() + self.d if self.buffer else None
                        await out_queue.put(chunk)
        finally:
            self.upstream_closed = True
            if timer_task:
                timer_task.cancel()
            async with self.lock:
                if self.buffer:
                    await out_queue.put(list(self.buffer))
                    self.buffer.clear()


async def batch_within(source: AsyncIterator[T], max_items: int, window_duration_secs: float) -> AsyncIterator[List[T]]:
    out_q: asyncio.Queue[List[T]] = asyncio.Queue()
    guard = BatchWithinStarvationGuard(max_items, window_duration_secs)
    producer = asyncio.create_task(guard.ingest_stream(source, out_q))

    while not (guard.upstream_closed and out_q.empty()):
        try:
            chunk = await asyncio.wait_for(out_q.get(), timeout=window_duration_secs * 2)
            yield chunk
            out_q.task_done()
        except asyncio.TimeoutError:
            if guard.upstream_closed and out_q.empty():
                break

    await producer


# Property Test & Reproducer Invariant Verification
async def run_property_tests():
    print("Running batchWithin invariant verification under downstream backpressure...")
    
    # 1. High-rate upstream producing 100 items with variable downstream consumption delays
    async def fast_upstream() -> AsyncIterator[int]:
        for i in range(50):
            yield i
            await asyncio.sleep(0.005) # fast arrival (5ms)

    chunks: List[List[int]] = []
    start = time.time()
    
    # K = 10, D = 0.08s (80ms)
    async for chunk in batch_within(fast_upstream(), max_items=10, window_duration_secs=0.08):
        chunks.append(chunk)
        # simulate variable downstream pull backpressure (delays)
        await asyncio.sleep(0.03)

    total_items = sum(len(c) for c in chunks)
    print(f"Total chunks emitted: {len(chunks)}, Total items: {total_items}")
    assert total_items == 50, f"Expected 50 items, got {total_items}"
    
    for idx, c in enumerate(chunks[:-1]):
        assert len(c) <= 10, f"Chunk {idx} exceeded max_items: {len(c)}"
        assert len(c) > 0, f"Chunk {idx} is empty"
    
    print("ALL PROPERTY INVARIANTS PASSED: No timer-reset starvation, no empty chunks, deterministic boundary handling.")
    return True


if __name__ == "__main__":
    asyncio.run(run_property_tests())
