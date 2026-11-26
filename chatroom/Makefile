CC ?= cc
CFLAGS ?= -std=c11 -O2 -Wall -Wextra -Wpedantic
CPPFLAGS += -D_POSIX_C_SOURCE=200809L

.PHONY: all clean

all: chat-server chat-client

chat-server: server.c chat.c chat.h
	$(CC) $(CPPFLAGS) $(CFLAGS) $(LDFLAGS) server.c chat.c -pthread -o $@

chat-client: client.c chat.c chat.h
	$(CC) $(CPPFLAGS) $(CFLAGS) $(LDFLAGS) client.c chat.c -o $@

clean:
	rm -f chat-server chat-client
