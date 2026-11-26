CC ?= cc
CFLAGS ?= -std=c11 -O2 -Wall -Wextra -Wpedantic
CPPFLAGS += -D_POSIX_C_SOURCE=200809L

.PHONY: all clean
all: .build/pipes .build/threads

.build:
	mkdir -p $@

.build/pipes: pipes.c | .build
	$(CC) $(CPPFLAGS) $(CFLAGS) $(LDFLAGS) $< -o $@

.build/threads: threads.c | .build
	$(CC) $(CPPFLAGS) $(CFLAGS) $(LDFLAGS) $< -pthread -o $@

clean:
	rm -f .build/pipes .build/threads
