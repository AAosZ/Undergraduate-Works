#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>
#include <errno.h>
#include <signal.h>
#include "io_helpers.h"
#include "commands.h"

Command *commands = NULL;
int process_count = 0;
int next_process_id = 1;

void init_process(void) {

}

void add_process(pid_t pid, const char *command) {
    if (process_count == 0) {
        next_process_id = 1;
    }

    Command new_process;
    new_process.process_id = next_process_id++;
    new_process.pid = pid;
    new_process.command = strdup(command);

    commands = realloc(commands, (process_count + 1) * sizeof(Command));
    commands[process_count++] = new_process;
}

void remove_process(pid_t pid) {
    for (int i = 0; i < process_count; i++) {
        if (commands[i].pid == pid) {
            free(commands[i].command);
            for (int j = i; j < process_count - 1; j++) {
                commands[j] = commands[j + 1];
            }
            process_count--;
            commands = realloc(commands, process_count * sizeof(Command));

            if (process_count == 0) {
                next_process_id = 1;
            }
            break;
        }
    }
}


void check_completed_process(void) {
    for (int i = 0; i < process_count; i++) {
        pid_t pid = commands[i].pid;
        int status;
        pid_t ret = waitpid(pid, &status, WNOHANG);

        if (ret == pid || ret == -1) {
            char done_msg[MAX_STR_LEN];
            snprintf(done_msg, sizeof(done_msg), "[%d]+  Done\n", commands[i].process_id);
            display_message(done_msg);

            char cmd_msg[MAX_STR_LEN];
            snprintf(cmd_msg, sizeof(cmd_msg), "%s\n", commands[i].command);
            display_message(cmd_msg);

            remove_process(pid);
            i--;
        }
    }
}

void print_process(void) {
    for (int i = 0; i < process_count; i++) {
        char msg[MAX_STR_LEN];
        snprintf(msg, sizeof(msg), "%s %d\n", commands[i].command, commands[i].pid);
        display_message(msg);
    }
}

int kill_process(pid_t pid, int signum) {
    if (kill(pid, 0) == -1) {
        if (errno == ESRCH) {
            return -1;
        }
        return -2;
    }
    if (kill(pid, signum) == -1) {
        if (errno == EINVAL) {
            return -3;
        }
        return -4;
    }
    return 0;
}