# Course Exercises

Short examples from ULB coursework, with the working and recovered versions identified below.

| Exercise | Source and status |
| --- | --- |
| [Process communication](posix/pipes.c) | Adapted from `exercice1.c`: a parent sends two integers through a pipe to a child and receives the sum through a second pipe. |
| [POSIX threads](posix/threads.c) | Adapted from `exercice2.c`: two workers print values independently and the main thread joins both. |
| [Preorder traversal](python/preorder.py) | Recovered from an incomplete exam draft. A working version compares recursion and an explicit stack over the original example tree. |
| [Tandem-free strings](python/tandem_free.py) | Adapted from `projetINFOF2061.py`: generate a toy string over four symbols and roll back any adjacent repeated block. |
| [Logic circuit](ok.circ) | Original Logisim file, with one circuit built from NAND gates. Open in Logisim 2.7.1 or a compatible version. |

```sh
make -C posix
printf '3 8\n' | posix/.build/pipes
posix/.build/threads
python3 python/preorder.py
python3 python/tandem_free.py 40 --seed 7
```

The local collection also contains TCP echo examples (single connection, threaded, and `select`), process-management corrections, course handouts, and a GitHub Classroom starter. Their authorship or status as personal submissions could not be established, so this edition lists them without reproducing their source or handouts.
