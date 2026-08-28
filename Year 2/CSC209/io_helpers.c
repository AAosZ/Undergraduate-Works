#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <stdio.h>

#include "io_helpers.h"
#include "variables.h"

void display_message(char *str) {
    write(STDOUT_FILENO, str, strnlen(str, MAX_STR_LEN));
}

void display_error(char *pre_str, char *str) {
    if (pre_str) {
        write(STDERR_FILENO, pre_str, strnlen(pre_str, MAX_STR_LEN));
    }
    if (str) {
        write(STDERR_FILENO, str, strnlen(str, MAX_STR_LEN));
    }
    write(STDERR_FILENO, "\n", 1);
}

ssize_t get_input(char *in_ptr) {
    int retval = read(STDIN_FILENO, in_ptr, MAX_STR_LEN);
    if (retval == -1) {
        return 0;
    }
    if (retval >= MAX_STR_LEN) {
        write(STDERR_FILENO, "ERROR: input line too long\n", strlen("ERROR: input line too long\n"));
        int junk;
        while ((junk = getchar()) != EOF && junk != '\n');
        in_ptr[0] = '\0';
        return -1;
    }
    in_ptr[retval] = '\0';
    return retval;
}

size_t tokenize_input(char *in_ptr, char **tokens) {
    expansion(in_ptr);

    char *curr_ptr = strtok (in_ptr, DELIMITERS);
    size_t token_count = 0;

    while (curr_ptr != NULL) {
        tokens[token_count++] = curr_ptr;
	curr_ptr = strtok(NULL, DELIMITERS);
    }
    tokens[token_count] = NULL;
    return token_count;
}
