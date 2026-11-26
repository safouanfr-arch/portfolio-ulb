#include <stdio.h>
#include <stdlib.h>
#include <sys/wait.h>
#include <unistd.h>

int main(void)
{
    int to_child[2], to_parent[2];
    if (pipe(to_child) < 0 || pipe(to_parent) < 0) {
        perror("pipe");
        return EXIT_FAILURE;
    }
    pid_t child = fork();
    if (child < 0) {
        perror("fork");
        return EXIT_FAILURE;
    }

    int a, b;
    if (child == 0) {
        close(to_child[1]);
        close(to_parent[0]);
        FILE *input = fdopen(to_child[0], "r");
        FILE *output = fdopen(to_parent[1], "w");
        if (input == NULL || output == NULL || fscanf(input, "%d%d", &a, &b) != 2) {
            return EXIT_FAILURE;
        }
        fprintf(output, "%lld\n", (long long)a + b);
        fclose(input);
        return fclose(output) == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
    }

    close(to_child[0]);
    close(to_parent[1]);
    FILE *output = fdopen(to_child[1], "w");
    FILE *input = fdopen(to_parent[0], "r");
    if (output == NULL || input == NULL) {
        perror("fdopen");
        return EXIT_FAILURE;
    }

    printf("Enter two integers: ");
    fflush(stdout);
    int supplied = scanf("%d%d", &a, &b) == 2 && fprintf(output, "%d %d\n", a, b) > 0;
    if (fclose(output) != 0) {
        supplied = 0;
    }

    long long sum;
    int received = supplied && fscanf(input, "%lld", &sum) == 1;
    fclose(input);

    int status;
    if (waitpid(child, &status, 0) < 0 || !WIFEXITED(status) || WEXITSTATUS(status) != 0 ||
        !received) {
        fprintf(stderr, "No result received. Enter two valid integers.\n");
        return EXIT_FAILURE;
    }

    printf("%d + %d = %lld\n", a, b, sum);
    return EXIT_SUCCESS;
}
