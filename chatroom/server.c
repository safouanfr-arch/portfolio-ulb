#include "chat.h"

#include <arpa/inet.h>
#include <errno.h>
#include <pthread.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <unistd.h>

enum { MAX_CLIENTS = 4, LINE_SIZE = MESSAGE_SIZE + NAME_SIZE + 64 };

typedef struct {
    int socket_fd;
    bool ready;
} Client;

static Client *clients[MAX_CLIENTS];
static pthread_mutex_t clients_lock = PTHREAD_MUTEX_INITIALIZER;

static bool queue_add(Client *client)
{
    bool added = false;
    pthread_mutex_lock(&clients_lock);
    for (size_t i = 0; i < MAX_CLIENTS; ++i) {
        if (clients[i] == NULL) {
            clients[i] = client;
            added = true;
            break;
        }
    }
    pthread_mutex_unlock(&clients_lock);
    return added;
}

static void queue_remove(Client *client)
{
    pthread_mutex_lock(&clients_lock);
    for (size_t i = 0; i < MAX_CLIENTS; ++i) {
        if (clients[i] == client) {
            clients[i] = NULL;
            break;
        }
    }
    pthread_mutex_unlock(&clients_lock);
}

static void broadcast(const char *message, const Client *sender)
{
    size_t length = strlen(message);
    pthread_mutex_lock(&clients_lock);
    for (size_t i = 0; i < MAX_CLIENTS; ++i) {
        Client *recipient = clients[i];
        if (recipient != NULL && recipient != sender && recipient->ready &&
            send_all(recipient->socket_fd, message, length) < 0) {
            shutdown(recipient->socket_fd, SHUT_RDWR);
        }
    }
    pthread_mutex_unlock(&clients_lock);
}

static void *handle_client(void *arg)
{
    Client *client = arg;
    FILE *input = fdopen(client->socket_fd, "r");
    char name[NAME_SIZE];
    char line[LINE_SIZE];
    const char welcome[] = "Welcome to discULB.\n";

    // The original protocol starts with a 32-byte, zero-padded username.
    if (input != NULL && fread(name, 1, sizeof(name), input) == sizeof(name) &&
        memchr(name, '\0', sizeof(name)) != NULL && valid_name(name)) {
        pthread_mutex_lock(&clients_lock);
        client->ready = send_all(client->socket_fd, welcome, sizeof(welcome) - 1) == 0;
        pthread_mutex_unlock(&clients_lock);
        if (!client->ready) {
            queue_remove(client);
            fclose(input);
            free(client);
            return NULL;
        }

        snprintf(line, sizeof(line), "%s joined the chat.\n", name);
        broadcast(line, client);

        while (fgets(line, sizeof(line), input) != NULL) {
            if (strchr(line, '\n') == NULL || strcmp(line, "exit\n") == 0) {
                break;
            }
            if (line[0] != '\n') {
                broadcast(line, client);
            }
        }

        queue_remove(client);
        snprintf(line, sizeof(line), "%s left the chat.\n", name);
        broadcast(line, client);
    } else {
        queue_remove(client);
    }

    if (input != NULL) {
        fclose(input);
    } else {
        close(client->socket_fd);
    }
    free(client);
    return NULL;
}

int main(int argc, char **argv)
{
    int port = argc == 2 ? parse_port(argv[1]) : -1;
    if (port < 0) {
        fprintf(stderr, "Usage: %s <port 1-65535>\n", argv[0]);
        return EXIT_FAILURE;
    }

    int listener = socket(AF_INET, SOCK_STREAM, 0);
    if (listener < 0) {
        perror("socket");
        return EXIT_FAILURE;
    }

    signal(SIGPIPE, SIG_IGN);
    int reuse = 1;
    struct sockaddr_in address = {
        .sin_family = AF_INET,
        .sin_port = htons((unsigned short)port),
        .sin_addr.s_addr = htonl(INADDR_LOOPBACK),
    };
    if (setsockopt(listener, SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(reuse)) < 0 ||
        bind(listener, (struct sockaddr *)&address, sizeof(address)) < 0 ||
        listen(listener, MAX_CLIENTS) < 0) {
        perror("server setup");
        close(listener);
        return EXIT_FAILURE;
    }

    printf("discULB listening on 127.0.0.1:%d\n", port);
    fflush(stdout);

    for (;;) {
        int socket_fd = accept(listener, NULL, NULL);
        if (socket_fd < 0) {
            if (errno == EINTR) {
                continue;
            }
            perror("accept");
            break;
        }

        struct timeval timeout = {.tv_sec = 1};
        if (setsockopt(socket_fd, SOL_SOCKET, SO_SNDTIMEO, &timeout, sizeof(timeout)) < 0) {
            perror("setsockopt");
            close(socket_fd);
            continue;
        }

        Client *client = malloc(sizeof(*client));
        if (client == NULL) {
            perror("malloc");
            close(socket_fd);
            continue;
        }
        *client = (Client){.socket_fd = socket_fd, .ready = false};
        if (!queue_add(client)) {
            const char full[] = "The chat is full. Try again later.\n";
            send_all(socket_fd, full, sizeof(full) - 1);
            close(socket_fd);
            free(client);
            continue;
        }

        pthread_t worker;
        int result = pthread_create(&worker, NULL, handle_client, client);
        if (result != 0) {
            fprintf(stderr, "pthread_create: %s\n", strerror(result));
            queue_remove(client);
            close(socket_fd);
            free(client);
            continue;
        }
        pthread_detach(worker);
    }

    close(listener);
    return EXIT_FAILURE;
}
