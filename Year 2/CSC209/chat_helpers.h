#ifndef CHAT_HELPERS_H
#define CHAT_HELPERS_H

struct client_sock {
    int sock_fd;
    int state;
    char *username;
    char buf[BUF_SIZE];
    int inbuf;
    struct client_sock *next;
};

int write_buf_to_client(struct client_sock *c, char *buf, int len);

int remove_client(struct client_sock **curr, struct client_sock **clients);

int read_from_client(struct client_sock *curr);

int set_username(struct client_sock *curr);

int run_server(int port);
int run_client(const char *hostname, int port);

#endif
