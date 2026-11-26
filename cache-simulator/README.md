# L1 Cache Simulator

A Python terminal program from the ULB INFO-F-102 computer architecture project. It models a fully associative cache with eight slots over a 32-cell main memory. For each instruction it prints the value, hit or miss, cache slot, and any dirty write-back.

## Run

Python 3.10 or newer, with only the standard library:

```sh
python3 cache_simulator.py example.txt
python3 -m unittest -v
```

Use `R ADDRESS` to read and `W VALUE ADDRESS` to write. Addresses run from 0 to 31. The cache fills empty slots before evicting the least recently used line. Writes allocate a line and mark it dirty. The updated value is written back only when that line is evicted.

The original exercise by Safouan Tassi included instructor-provided trace formatters. This edition keeps the instruction format and core exercise, uses independent trace formatting, and tests the behavior of empty slots and dirty evictions.
