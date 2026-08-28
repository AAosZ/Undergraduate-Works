#ifndef __COMMANDS_H__
#define __COMMANDS_H__
#include <sys/types.h>

typedef struct Command {
    int process_id;
    pid_t pid;
    char *command;
} Command;

void init_process(void);
void add_process(pid_t pid, const char *command);
void remove_process(pid_t pid);
void check_completed_process(void);
void print_process(void);
int kill_process(pid_t pid, int signum);
extern int next_process_id;
extern Command *commands;
extern int process_count;
extern int next_process_id;
#endif