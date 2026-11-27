# ULB Programming Portfolio

Selected work from my computer science studies at the Universite libre de Bruxelles, with instructions and small demos for running it today.

| Project | What it shows |
| --- | --- |
| [discULB Chatroom](chatroom/) | TCP sockets in C, one server thread per client, and synchronized message broadcasting |
| [Cache Simulator](cache-simulator/) | L1 cache hits and misses, LRU replacement, and dirty write-back in Python |
| [JPEG Compressor](jpeg-compressor/) | Bash argument parsing, recursive file processing, and ImageMagick |
| [Castle Escape](turtle-maze/) | A Turtle game with grid movement, an inventory clue, and a locked door |
| [Course Exercises](exercises/) | POSIX pipes, threads, Python algorithms, and a Logisim circuit |

Each directory includes its own run instructions. The READMEs identify the original coursework, collaborators or teaching material where relevant, and the changes made for this edition.

The Linux workflow runs the existing cache, maze, chatroom and JPEG tests and compiles the standalone POSIX exercises. The maze tests cover game logic without a graphical display. [Lab CI workflow](.github/workflows/ci.yml)
