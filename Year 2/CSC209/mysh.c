#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <unistd.h>
#include <signal.h>
#include <sys/wait.h>
#include <limits.h>

#include "builtins.h"
#include "io_helpers.h"
#include "variables.h"
#include "commands.h"

char *find_command_path(const char *cmd) {
    const char *dirs[] = {"/bin", "/usr/bin"};
    for (int i = 0; i < 2; i++) {
        char path[PATH_MAX];
        snprintf(path, sizeof(path), "%s/%s", dirs[i], cmd);
        if (access(path, X_OK) == 0) {
            return strdup(path);
        }
    }
    return NULL;
}

char *join_tokens(char **tokens) {
    if (tokens == NULL || tokens[0] == NULL) {
        return NULL;
    }

    size_t total_length = 0;
    for (int i = 0; tokens[i] != NULL; i++) {
        total_length += strlen(tokens[i]) + 1;
    }

    char *result = malloc(total_length);
    if (result == NULL) {
        perror("malloc");
        return NULL;
    }

    result[0] = '\0';
    for (int i = 0; tokens[i] != NULL; i++) {
        strcat(result, tokens[i]);
        if (tokens[i + 1] != NULL) {
            strcat(result, " ");
        }
    }

    return result;
}

int main() {
    signal(SIGINT, SIG_IGN);
    init_process();

    char *prompt = "mysh$ ";
    char input_buf[MAX_STR_LEN + 1];
    input_buf[MAX_STR_LEN] = '\0';
    char *token_arr[MAX_STR_LEN] = {NULL};

    while (1) {
        check_completed_process();
        display_message(prompt);
        int ret = get_input(input_buf);
        if (ret == -1) {
            break;
        }

        size_t token_count = tokenize_input(input_buf, token_arr);
        if (token_count == 0) {
            continue;
        }

        if (strcmp(token_arr[0], "exit") == 0) {
            break;
        }

        int has_pipe = 0;
        for (int i = 0; token_arr[i] != NULL; i++) {
            if (strcmp(token_arr[i], "|") == 0) {
                has_pipe = 1;
                break;
            }
        }



        if (has_pipe) {
            int background = 0;
            if (token_count > 0 && strcmp(token_arr[token_count - 1], "&") == 0) {
                background = 1;
                token_arr[token_count - 1] = NULL;
                token_count--;
            }

            int cmd_start = 0;
            int num_commands = 0;
            char ***commands = NULL;

            for (int i = 0; ; i++) {
                if (token_arr[i] == NULL || strcmp(token_arr[i], "|") == 0) {
                    int cmd_len = i - cmd_start;
                    char **cmd = malloc((cmd_len + 1) * sizeof(char *));
                    for (int j = 0; j < cmd_len; j++) {
                        cmd[j] = token_arr[cmd_start + j];
                    }
                    cmd[cmd_len] = NULL;

                    commands = realloc(commands, (num_commands + 1) * sizeof(char **));
                    commands[num_commands++] = cmd;

                    if (token_arr[i] == NULL) break;
                    cmd_start = i + 1;
                }
            }

            int *is_builtin = malloc(num_commands * sizeof(int));
            for (int i = 0; i < num_commands; i++) {
                bn_ptr fn = check_builtin(commands[i][0]);
                is_builtin[i] = (fn != NULL);
            }

            int num_pipes = num_commands - 1;
            int (*pipes)[2] = malloc(num_pipes * sizeof(int[2]));

            for (int i = 0; i < num_pipes; i++) {
                if (pipe(pipes[i]) == -1) {
                    perror("pipe");
                    exit(EXIT_FAILURE);
                }
            }

            pid_t pids[num_commands];
            for (int i = 0; i < num_commands; i++) {
                pids[i] = fork();
                if (pids[i] == -1) {
                    perror("fork");
                    exit(EXIT_FAILURE);
                } else if (pids[i] == 0) {
                    signal(SIGINT, SIG_DFL);

                    if (i > 0) {
                        dup2(pipes[i-1][0], STDIN_FILENO);
                        close(pipes[i-1][0]);
                    }
                    if (i < num_commands - 1) {
                        dup2(pipes[i][1], STDOUT_FILENO);
                        close(pipes[i][1]);
                    }
                    for (int j = 0; j < num_pipes; j++) {
                        close(pipes[j][0]);
                        close(pipes[j][1]);
                    }

                    char **cmd = commands[i];
                    bn_ptr builtin_fn = check_builtin(cmd[0]);
                    if (builtin_fn != NULL) {
                        ssize_t ret = builtin_fn(cmd);
                        exit(ret == 0 ? EXIT_SUCCESS : EXIT_FAILURE);
                    } else {
                        char *path = find_command_path(cmd[0]);
                        if (path == NULL) {
                            display_error("ERROR: Unknown command: ", cmd[0]);
                            exit(EXIT_FAILURE);
                        }
                        execv(path, cmd);
                        perror("execv");
                        exit(EXIT_FAILURE);
                    }
                }
            }

            for (int i = 0; i < num_pipes; i++) {
                close(pipes[i][0]);
                close(pipes[i][1]);
            }
            free(pipes);

            if (!background) {
                for (int i = 0; i < num_commands; i++) {
                    int status;
                    waitpid(pids[i], &status, 0);
                    if (WIFEXITED(status)) {
                        int exit_status = WEXITSTATUS(status);
                        if (exit_status != EXIT_SUCCESS && is_builtin[i]) {
                            display_error("ERROR: Builtin failed: ", commands[i][0]);
                        }
                    }
                }
            }

            else {
                char *command = join_tokens(token_arr);
                add_process(pids[num_commands - 1], command);
                char msg[MAX_STR_LEN];
                snprintf(msg, sizeof(msg), "[%d] %d\n", next_process_id - 1, pids[num_commands - 1]);
                display_message(msg);
                free(command);
            }

            for (int i = 0; i < num_commands; i++) {
                free(commands[i]);
            }

            free(commands);
            free(is_builtin);

            continue;
        }





        if (token_arr[0] != NULL && strchr(token_arr[0], '=') != NULL) {
            char *assignment = strdup(token_arr[0]);
            if (!assignment) {
                fprintf(stderr, "ERROR: Memory allocation failed");
                continue;
            }

            char *name = assignment;
            char *value = strchr(assignment, '=');
            if (value) {
                *value = '\0';
                value++;
                set_variable(name, value);
            } else {
                fprintf(stderr, "ERROR: Invalid variable assignment");
            }

            free(assignment);
            continue;
        }





        int background = 0;
        if (token_count > 0 && strcmp(token_arr[token_count - 1], "&") == 0) {
            background = 1;
            token_arr[token_count - 1] = NULL;
            token_count--;
        }

        bn_ptr builtin_fn = check_builtin(token_arr[0]);
        if (builtin_fn != NULL) {
            if (background) {
                pid_t pid = fork();
                if (pid == -1) {
                    perror("fork");
                } else if (pid == 0) {
                    signal(SIGINT, SIG_DFL);
                    ssize_t ret = builtin_fn(token_arr);
                    exit(ret == 0 ? EXIT_SUCCESS : EXIT_FAILURE);
                } else {
                    char *command = join_tokens(token_arr);
                    add_process(pid, command);
                    char msg[MAX_STR_LEN];
                    snprintf(msg, sizeof(msg), "[%d] %d\n", next_process_id - 1, pid);
                    display_message(msg);
                    free(command);
                }
            } else {
                ssize_t err = builtin_fn(token_arr);
                if (err == -1) {
                    display_error("ERROR: Builtin failed: ", token_arr[0]);
                }
            }
        } else {
            pid_t pid = fork();
            if (pid == -1) {
                perror("fork");
            } else if (pid == 0) {
                signal(SIGINT, SIG_DFL);
                char *path = find_command_path(token_arr[0]);
                if (path == NULL) {
                    display_error("ERROR: Unknown command: ", token_arr[0]);
                    exit(EXIT_FAILURE);
                }
                execv(path, token_arr);
                perror("execv");
                exit(EXIT_FAILURE);
            } else {
                if (!background) {
                    waitpid(pid, NULL, 0);
                } else {
                    char *command = join_tokens(token_arr);
                    add_process(pid, command);
                    char msg[MAX_STR_LEN];
                    snprintf(msg, sizeof(msg), "[%d] %d\n", next_process_id - 1, pid);
                    display_message(msg);
                    free(command);
                }
            }
        }
    }





    free_variables();
    return 0;
}