#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

enum { REPETITIONS = 100 };

static void *print_number(void *argument)
{
    const int *number = argument;
    for (int i = 0; i < REPETITIONS; ++i) {
        printf("%d\n", *number);
    }
    return NULL;
}

int main(void)
{
    int numbers[] = {1, 2};
    pthread_t workers[2];
    size_t started = 0;
    int result = EXIT_SUCCESS;

    for (; started < 2; ++started) {
        int error = pthread_create(&workers[started], NULL, print_number, &numbers[started]);
        if (error != 0) {
            fprintf(stderr, "pthread_create: %s\n", strerror(error));
            result = EXIT_FAILURE;
            break;
        }
    }

    for (size_t i = 0; i < started; ++i) {
        int error = pthread_join(workers[i], NULL);
        if (error != 0) {
            fprintf(stderr, "pthread_join: %s\n", strerror(error));
            result = EXIT_FAILURE;
        }
    }
    if (result == EXIT_SUCCESS) {
        puts("Both threads finished.");
    }
    return result;
}
