#ifndef __BUILTINS_H__
#define __BUILTINS_H__

#include <unistd.h>

typedef ssize_t (*bn_ptr)(char **);
ssize_t bn_echo(char **tokens);
ssize_t bn_exit(char **tokens);
ssize_t bn_cd(char **tokens);
ssize_t bn_ls(char **tokens);
ssize_t bn_wc(char **tokens);
ssize_t bn_cat(char **tokens);
ssize_t bn_kill(char **tokens);
ssize_t bn_ps(char **tokens);
ssize_t bn_start_server(char **tokens);
ssize_t bn_close_server(char **tokens);
ssize_t bn_send(char **tokens);
ssize_t bn_start_client(char **tokens);


bn_ptr check_builtin(const char *cmd);


static const char * const BUILTINS[] = {"echo", "exit", "ls", "cd", "cat", "wc", "kill", "ps", "start-server", "close-server", "send", "start-client"};
static const bn_ptr BUILTINS_FN[] = {bn_echo, bn_exit, bn_ls, bn_cd, bn_cat, bn_wc, bn_kill, bn_ps, bn_start_server, bn_close_server, bn_send, bn_start_client, NULL};    // Extra null element for 'non-builtin'
static const ssize_t BUILTINS_COUNT = sizeof(BUILTINS) / sizeof(char *);

#endif
