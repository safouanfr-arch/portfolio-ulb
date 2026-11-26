"""Trace a fully associative L1 cache with LRU replacement."""

import argparse
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CacheLine:
    address: int
    value: int
    last_used: int
    dirty: bool = False


@dataclass(frozen=True)
class Access:
    operation: str
    address: int
    value: int
    slot: int
    hit: bool
    write_back: tuple[int, int] | None

    def __str__(self):
        direction = "from" if self.operation == "RD" else "to"
        outcome = "hit" if self.hit else "miss"
        trace = f"{self.operation} {self.value} {direction} {self.address} | {outcome}, slot {self.slot}"
        if self.write_back is not None:
            address, value = self.write_back
            trace += f" | write back {value} to {address}"
        return trace


class Cache:
    def __init__(self, memory_size=32, slots=8):
        if memory_size < 1 or slots < 1:
            raise ValueError("memory and cache sizes must be positive")
        self.memory = [0] * memory_size
        self.lines: list[CacheLine | None] = [None] * slots
        self.clock = 0

    def access(self, address: int, value: int | None = None) -> Access:
        if not 0 <= address < len(self.memory):
            raise ValueError(f"address {address} is outside 0..{len(self.memory) - 1}")

        self.clock += 1
        write_back = None
        for slot, line in enumerate(self.lines):
            if line is not None and line.address == address:
                hit = True
                break
        else:
            hit = False
            slot = min(
                range(len(self.lines)),
                key=lambda index: -1 if self.lines[index] is None else self.lines[index].last_used,
            )
            victim = self.lines[slot]
            if victim is not None and victim.dirty:
                self.memory[victim.address] = victim.value
                write_back = (victim.address, victim.value)
            line = CacheLine(address, self.memory[address], self.clock)
            self.lines[slot] = line

        line.last_used = self.clock
        if value is not None:
            line.value = value
            line.dirty = True

        return Access("RD" if value is None else "WR", address, line.value, slot, hit, write_back)


def run_trace(lines, cache):
    for number, raw_line in enumerate(lines, start=1):
        fields = raw_line.partition("#")[0].split()
        if not fields:
            continue
        try:
            match fields:
                case ["R", address]:
                    yield cache.access(int(address))
                case ["W", value, address]:
                    yield cache.access(int(address), int(value))
                case _:
                    raise ValueError("expected R ADDRESS or W VALUE ADDRESS")
        except ValueError as error:
            raise ValueError(f"line {number}: {error}") from error


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trace", type=Path, help="text file containing reads and writes")
    args = parser.parse_args()

    try:
        with args.trace.open(encoding="utf-8") as trace:
            for access in run_trace(trace, Cache()):
                print(access)
    except (OSError, ValueError) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
