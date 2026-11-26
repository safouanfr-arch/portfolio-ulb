#include "chat.h"

#include <arpa/inet.h>
#include <errno.h>
#include <poll.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <time.h>
#include <unistd.h>

static int send_line(int socket_fd, const char *name, const char *message)
{
    char timestamp[20] = "time unavailable";
    struct tm local;
    time_t now = time(NULL);
    if (localtime_r(&now, &local) != NULL) {
        strftime(timestamp, sizeof(timestamp), "%H:%M:%S", &local);
    }

    char line[MESSAGE_SIZE + NAME_SIZE + 64];
    int length = snprintf(line, sizeof(line), "[%s] %s: %s\n", timestamp, name, message);
    return send_all(socket_fd, line, (size_t)length);
}

static int chat(int socket_fd, const char *name)
{
    struct pollfd events[] = {
        {.fd = socket_fd, .events = POLLIN},
        {.fd = STDIN_FILENO, .events = POLLIN},
    };
    char message[MESSAGE_SIZE + 1];
    size_t used = 0;
    bool overflow = false;

    for (;;) {
        if (poll(events, 2, -1) < 0) {
            if (errno == EINTR) {
                continue;
            }
            perror("poll");
            return EXIT_FAILURE;
        }

        char data[1024];
        if (events[0].revents != 0) {
            ssize_t count = recv(socket_fd, data, sizeof(data), 0);
            if (count <= 0) {
                return count == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
            }
            fwrite(data, 1, (size_t)count, stdout);
            fflush(stdout);
        }

        if (events[1].revents != 0) {
            ssize_t count = read(STDIN_FILENO, data, sizeof(data));
            if (count < 0 && errno == EINTR) {
                continue;
            }
            if (count <= 0) {
                if (count == 0 && used > 0 && !overflow) {
                    message[used] = '\0';
                    if (strcmp(message, "exit") != 0 && send_line(socket_fd, name, message) < 0) {
                        return EXIT_FAILURE;
                    }
                }
                return count == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
            }

            for (ssize_t i = 0; i < count; ++i) {
                if (data[i] == '\n') {
                    message[used] = '\0';
                    if (overflow) {
                        fprintf(stderr, "Message exceeds %d bytes.\n", MESSAGE_SIZE);
                    } else if (strcmp(message, "exit") == 0) {
                        return EXIT_SUCCESS;
                    } else if (used > 0 && send_line(socket_fd, name, message) < 0) {
                        return EXIT_FAILURE;
                    }
                    used = 0;
                    overflow = false;
                } else if (used == MESSAGE_SIZE) {
                    overflow = true;
                } else {
                    message[used++] = data[i];
                }
            }
        }
    }
}

int main(int argc, char **argv)
{
    int port = argc == 4 ? parse_port(argv[3]) : -1;
    struct sockaddr_in server = {.sin_family = AF_INET, .sin_port = htons((unsigned short)port)};
    if (port < 0 || !valid_name(argv[1]) || inet_pton(AF_INET, argv[2], &server.sin_addr) != 1) {
        fprintf(stderr, "Usage: %s <username (2-31 bytes)> <IPv4 address> <port>\n", argv[0]);
        return EXIT_FAILURE;
    }

    signal(SIGPIPE, SIG_IGN);
    int socket_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (socket_fd < 0) {
        perror("socket");
        return EXIT_FAILURE;
    }
    if (connect(socket_fd, (struct sockaddr *)&server, sizeof(server)) < 0) {
        perror("connect");
        close(socket_fd);
        return EXIT_FAILURE;
    }

    char name[NAME_SIZE] = {0};
    memcpy(name, argv[1], strlen(argv[1]));
    if (send_all(socket_fd, name, sizeof(name)) < 0) {
        perror("send username");
        close(socket_fd);
        return EXIT_FAILURE;
    }

    printf("Connected as %s. Type a message or 'exit'.\n", name);
    fflush(stdout);
    int result = chat(socket_fd, name);
    close(socket_fd);
    return result;
}
