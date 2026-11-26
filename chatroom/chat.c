#include "chat.h"

#include <ctype.h>
#include <errno.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>

int parse_port(const char *value)
{
    if (*value == '\0' || strspn(value, "0123456789") != strlen(value)) {
        return -1;
    }

    long port = strtol(value, NULL, 10);
    return port >= 1 && port <= 65535 ? (int)port : -1;
}

bool valid_name(const char *name)
{
    size_t length = strlen(name);
    if (length < 2 || length >= NAME_SIZE) {
        return false;
    }

    for (size_t i = 0; i < length; ++i) {
        if (iscntrl((unsigned char)name[i])) {
            return false;
        }
    }
    return true;
}

int send_all(int socket_fd, const void *data, size_t length)
{
    const char *cursor = data;
    while (length != 0) {
        ssize_t sent = send(socket_fd, cursor, length, 0);
        if (sent < 0 && errno == EINTR) {
            continue;
        }
        if (sent <= 0) {
            return -1;
        }
        cursor += sent;
        length -= (size_t)sent;
    }
    return 0;
}
