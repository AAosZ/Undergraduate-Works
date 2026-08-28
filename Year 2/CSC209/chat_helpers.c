#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "socket.h"
#include "chat_helpers.h"

int write_buf_to_client(struct client_sock *c, char *buf, int len) {
    if (len <= 0) return 1;

    if (buf[len - 1] != '\n') {
        if (len + 2 >= BUF_SIZE) return 1;
        buf[len] = '\r';
        buf[len + 1] = '\n';
        buf[len + 2] = '\0';
        len += 2;
    }

    fflush(stdout);

    return write_to_socket(c->sock_fd, buf, len);
}

int remove_client(struct client_sock **curr, struct client_sock **clients) {
    if (*curr == NULL || *clients == NULL) {
        return 1;
    }

    struct client_sock *prev = NULL;
    struct client_sock *c = *clients;

    while (c != NULL && c != *curr) {
        prev = c;
        c = c->next;
    }

    if (c == NULL) {
        return 1;
    }

    if (prev == NULL) {
        *clients = c->next;
    } else {
        prev->next = c->next;
    }

    *curr = c->next;

    free(c->username);
    free(c);

    return 0;
}

int read_from_client(struct client_sock *curr) {
    return read_from_socket(curr->sock_fd, curr->buf, &(curr->inbuf));
}

int set_username(struct client_sock *curr) {
    char *msg;

    if (get_message(&msg, curr->buf, &(curr->inbuf)) != 0) {
        return 1;
    }

    int len = strlen(msg);
    if (len >= 2 && msg[len-2] == '\r' && msg[len-1] == '\n') {
        msg[len-2] = '\0';
    }

    for (int i = 0; msg[i] != '\0'; i++) {
        if (msg[i] == ' ') {
            free(msg);
            return 1;
        }
    }

    curr->username = msg;
    return 0;
}
