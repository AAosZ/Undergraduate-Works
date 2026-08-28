#include <string.h>
#include <stdlib.h>
#include <dirent.h>
#include <stdbool.h>
#include <stdio.h>
#include <signal.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#include "builtins.h"
#include "io_helpers.h"
#include "variables.h"
#include "commands.h"
#include "chat_server.h"

extern Command *commands;
extern int process_count;
extern int next_process_id;

bn_ptr check_builtin(const char *cmd) {
    if (cmd == NULL) {
        display_error("ERROR: Missing command", "");
        return 0;
    }
    ssize_t cmd_num = 0;
    while (cmd_num < BUILTINS_COUNT &&
           strncmp(BUILTINS[cmd_num], cmd, MAX_STR_LEN) != 0) {
        cmd_num += 1;
    }
    return BUILTINS_FN[cmd_num];
}

ssize_t bn_echo(char **tokens) {
    ssize_t index = 1;

    if (tokens[index] != NULL) {
        display_message(tokens[index]);
        index += 1;
    }

    while (tokens[index] != NULL) {
        display_message(" ");
        display_message(tokens[index]);
        index += 1;
    }
    display_message("\n");

    return 0;
}

ssize_t bn_exit(char **tokens) {
    (void)tokens;
    exit(0);
    return 0;
}

void recursive_traversal(const char *path, const char *filter, int depth, int curr_depth) {
    if (depth != -1 && curr_depth > depth) {
        return;
    }

    DIR *dir = opendir(path);
    if (!dir) {
        display_error("ERROR: Invalid path", "");
        return;
    }

    struct dirent *entry;
    while ((entry = readdir(dir)) != NULL) {
        if (filter == NULL || strstr(entry->d_name, filter)) {
            display_message((char *)entry->d_name);
            display_message("\n");
        }

        if (entry->d_type == DT_DIR && strcmp(entry->d_name, ".") != 0 && strcmp(entry->d_name, "..") != 0) {
            size_t next_path_len = strlen(path) + strlen(entry->d_name) + 2;
            char *next_path = malloc(next_path_len);

            if (!next_path) {
                display_error("ERROR: Memory allocation error", "");
                closedir(dir);
                return;
            }

            snprintf(next_path, next_path_len, "%s/%s", path, entry->d_name);
            recursive_traversal(next_path, filter, depth, curr_depth + 1);
            free(next_path);
        }
    }

    closedir(dir);
}

ssize_t bn_ls(char **tokens) {
    char *filter = NULL;
    char *path = ".";
    bool isRecursive = false;
    int depth = -1;

    for (int i = 0; tokens[i] != NULL; i++) {
        if (strcmp(tokens[i], "--f") == 0) {
            if (tokens[i + 1] != NULL) {
                filter = tokens[++i];
            }

            else {
                display_error("ERROR: Missing substring for --f flag", "");
                return -1;
            }
        }

        else if (strcmp(tokens[i], "--rec") == 0) {
            isRecursive = true;
        }

        else if (strcmp(tokens[i], "--d") == 0) {
            if (tokens[i + 1] != NULL && atoi(tokens[i + 1]) > 0) {
                depth = atoi(tokens[++i]);
            }

            else {
                display_error("ERROR: Missing/Invalid value for --d flag", "");
                return -1;
            }
        }

        else {
            path = tokens[i];
        }
    }

    if (depth != -1 && !isRecursive) {
        display_error("ERROR: Invalid flags.", "");
    }

    DIR *dir = opendir(path);
    if (!dir) {
        display_error("ERROR: Invalid path", "");
        return -1;
    }

    struct dirent *entry;
    while ((entry = readdir(dir)) != NULL) {
        if (filter == NULL || strstr(entry->d_name, filter)) {
            display_message(entry->d_name);
            display_message("\n");
        }

        if (isRecursive && entry->d_type == DT_DIR && strcmp(entry->d_name, ".") != 0 && strcmp(entry->d_name, "..") != 0) {
            size_t new_path_len = strlen(path) + strlen(entry->d_name) + 2;
            char *new_path = malloc(new_path_len);
            if (!new_path) {
                display_error("ERROR: Memory allocation error", "");
                closedir(dir);
                return -1;
            }

            snprintf(new_path, new_path_len, "%s/%s", path, entry->d_name);
            recursive_traversal(new_path, filter, depth, 1);
            free(new_path);
        }
    }

    closedir(dir);
    return 0;
}

ssize_t bn_cd(char **tokens) {
    if (tokens == NULL) {
        display_error("ERROR: Missing tokens array", "");
    }

    char *path = tokens[1];

    if (tokens[2] != NULL) {
        display_error("ERROR: Too many arguments", "");
        return -1;
    }

    if (path == NULL) {
        char *home = getenv("HOME");

        if (home == NULL) {
            display_error("ERROR: Missing home environment variable", "");
            return -1;
        }

        if (chdir(home) != 0) {
            display_error("ERROR: Failed to change directory", "");
            return -1;
        }

        return 0;
    }

    if (chdir(path) != 0) {
        display_error("ERROR: Invalid path.", "");
        return -1;
    }

    return 0;
}

ssize_t bn_cat(char **tokens) {
    FILE *file = NULL;
    char *filename = NULL;
    int is_stdin = 0;

    if (tokens[1] != NULL) {
        if (tokens[2] != NULL) {
            display_error("ERROR: Too many arguments.", "");
            return -1;
        }
        filename = tokens[1];
        file = fopen(filename, "r");
        if (file == NULL) {
            display_error("ERROR: Cannot open file", "");
            return -1;
        }
    } else {
        if (isatty(STDIN_FILENO)) {
            display_error("ERROR: No input source provided", "");
            return -1;
        }
        file = stdin;
        is_stdin = 1;
    }

    char line[MAX_STR_LEN];
    while (fgets(line, MAX_STR_LEN, file) != NULL) {
        display_message(line);
    }
    fflush(stdout);

    if (!is_stdin) {
        fclose(file);
    }

    return 0;
}


ssize_t bn_wc(char **tokens) {
    FILE *file = NULL;
    char *filename = NULL;
    int is_stdin = 0;

    if (tokens[1] != NULL) {
        if (tokens[2] != NULL) {
            display_error("ERROR: Too many arguments.", "");
            return -1;
        }
        filename = tokens[1];
        file = fopen(filename, "r");
        if (file == NULL) {
            display_error("ERROR: Cannot open file", "");
            return -1;
        }
    } else {
        if (isatty(STDIN_FILENO)) {
            display_error("ERROR: No input source provided", "");
            return -1;
        }
        file = stdin;
        is_stdin = 1;
    }

    int word_count = 0;
    int character_count = 0;
    int newline_count = 0;
    char line[MAX_STR_LEN];

    while (fgets(line, MAX_STR_LEN, file)) {
        bool in_word = false;

        for (int i = 0; line[i] != '\0'; i++) {
            character_count++;
            if (line[i] == '\n') {
                newline_count++;
            }
            if (line[i] == ' ' || line[i] == '\t' || line[i] == '\n' || line[i] == '\r') {
                if (in_word) {
                    word_count++;
                    in_word = false;
                }
            } else {
                in_word = true;
            }
        }

        if (in_word) {
            word_count++;
        }
    }

    char buffer[MAX_STR_LEN];
    snprintf(buffer, MAX_STR_LEN, "word count %d\n", word_count);
    display_message(buffer);
    snprintf(buffer, MAX_STR_LEN, "character count %d\n", character_count);
    display_message(buffer);
    snprintf(buffer, MAX_STR_LEN, "newline count %d\n", newline_count);
    display_message(buffer);

    if (!is_stdin) {
        fclose(file);
    }

    return 0;
}


ssize_t bn_kill(char **tokens) {
    if (tokens[1] == NULL) {
        display_error("ERROR: Missing PID", "");
        return -1;
    }

    char *endptr;
    pid_t pid = strtol(tokens[1], &endptr, 10);
    if (*endptr != '\0') {
        display_error("ERROR: Invalid PID", "");
        return -1;
    }

    int signum = SIGTERM;
    if (tokens[2] != NULL) {
        signum = strtol(tokens[2], &endptr, 10);
        if (*endptr != '\0' || signum < 1 || signum >= NSIG) {
            display_error("ERROR: Invalid signal specified", "");
            return -1;
        }
    }

    int result = kill_process(pid, signum);
    switch (result) {
        case -1:
            display_error("ERROR: The process does not exist", "");
        return -1;
        case -3:
            display_error("ERROR: Invalid signal specified", "");
        return -1;
        default:
            return 0;
    }
}


ssize_t bn_ps(char **tokens) {
    (void)tokens;
    print_process();
    return 0;
}


ssize_t bn_start_server(char **tokens) {
    if (!tokens[1]) {
        display_error("ERROR: No port provided", "");
        return -1;
    }
    int port = atoi(tokens[1]);
    if (port <= 0) {
        display_error("ERROR: Invalid port", "");
        return -1;
    }

    pid_t pid = fork();
    if (pid == 0) {
        run_server(port);
        exit(0);
    } else if (pid > 0) {
        add_process(pid, "server");

        signal(SIGCHLD, SIG_IGN);
        return 0;
    } else {
        perror("fork");
        return -1;
    }
}

ssize_t bn_close_server(char **tokens) {
    (void)tokens;
    for (int i = 0; i < process_count; i++) {
        if (strcmp(commands[i].command, "server") == 0) {
            if (kill_process(commands[i].pid, SIGTERM) == 0) {
                remove_process(commands[i].pid);
                return 0;
            }
        }
    }
    display_error("ERROR: Server not running", "");
    return -1;
}

ssize_t bn_send(char **tokens) {
    if (!tokens[1] || !tokens[2] || !tokens[3]) {
        display_error("ERROR: Missing arguments", "");
        return -1;
    }

    int port = atoi(tokens[1]);
    char *host = tokens[2];

    char message[BUF_SIZE];
    size_t pos = 0;
    for (int i = 3; tokens[i]; ++i) {
        int written = snprintf(message + pos, sizeof(message) - pos, "%s%s",
                               tokens[i], tokens[i + 1] ? " " : "");
        if (written < 0 || (size_t)written >= sizeof(message) - pos) {
            display_error("ERROR: Message too long", "");
            return -1;
        }
        pos += written;
    }

    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) {
        perror("socket");
        return -1;
    }

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(port);

    if (inet_pton(AF_INET, host, &addr.sin_addr) <= 0) {
        perror("inet_pton");
        close(sock);
        return -1;
    }

    if (connect(sock, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
        perror("connect");
        close(sock);
        return -1;
    }

    const char *username = "shell\r\n";
    if (write_to_socket(sock, (char *)username, strlen(username)) != 0) {
        close(sock);
        return -1;
    }


    char message_line[BUF_SIZE + 3];
    snprintf(message_line, sizeof(message_line), "%s\r\n", message);
    if (write_to_socket(sock, message_line, strlen(message_line)) != 0) {
        close(sock);
        return -1;
    }

    close(sock);
    return 0;
}


ssize_t bn_start_client(char **tokens) {
    if (!tokens[1] || !tokens[2]) {
        display_error("ERROR: Missing port/hostname", "");
        return -1;
    }

    int port = atoi(tokens[1]);
    char *host = tokens[2];

    pid_t pid = fork();
    if (pid == 0) {
        char port_str[16];
        snprintf(port_str, sizeof(port_str), "%d", port);

        char *args[] = { "./chat_client", host, port_str, NULL };
        execv(args[0], args);
        perror("execv failed");
        exit(1);
    } else if (pid > 0) {
        add_process(pid, "client");
        return 0;
    } else {
        perror("fork");
        return -1;
    }
}