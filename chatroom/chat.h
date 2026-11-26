#ifndef CHAT_H
#define CHAT_H

#include <stdbool.h>
#include <stddef.h>

enum { NAME_SIZE = 32, MESSAGE_SIZE = 2048 };

int parse_port(const char *value);
bool valid_name(const char *name);
int send_all(int socket_fd, const void *data, size_t length);

#endif
