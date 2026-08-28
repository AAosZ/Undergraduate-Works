#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <errno.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <netinet/in.h>

#include "socket.h"

void setup_server_socket(struct listen_sock *s, int port) {
    if (!(s->addr = malloc(sizeof(struct sockaddr_in)))) {
        perror("malloc");
        exit(1);
    }
    s->addr->sin_family = AF_INET;
    s->addr->sin_port = htons(port);
    memset(&(s->addr->sin_zero), 0, 8);
    s->addr->sin_addr.s_addr = INADDR_ANY;

    s->sock_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (s->sock_fd < 0) {
        perror("server socket");
        free(s->addr);
        exit(1);
    }

    int on = 1;
    if (setsockopt(s->sock_fd, SOL_SOCKET, SO_REUSEADDR, &on, sizeof(on)) < 0) {
        perror("setsockopt");
        close(s->sock_fd);
        free(s->addr);
        exit(1);
    }

    if (bind(s->sock_fd, (struct sockaddr *)s->addr, sizeof(*(s->addr))) < 0) {
        perror("server: bind");
        close(s->sock_fd);
        free(s->addr);
        exit(1);
    }

    if (listen(s->sock_fd, MAX_BACKLOG) < 0) {
        perror("server: listen");
        close(s->sock_fd);
        free(s->addr);
        exit(1);
    }
}

int find_network_newline(const char *buf, int inbuf) {
    for (int i = 0; i < inbuf - 1; i++) {
        if (buf[i] == '\r' && buf[i + 1] == '\n') {
            return i + 2;
        }
    }
    return -1;
}

int read_from_socket(int sock_fd, char *buf, int *inbuf) {
    int bytes_read = read(sock_fd, buf + *inbuf, BUF_SIZE - *inbuf);
    if (bytes_read < 0) {
        perror("read");
        return -1;
    }
    if (bytes_read == 0) {
        return 1;
    }

    *inbuf += bytes_read;

    if (find_network_newline(buf, *inbuf) != -1) {
        return 0;
    }

    return 2;
}

int get_message(char **dst, char *src, int *inbuf) {
    int msg_end = find_network_newline(src, *inbuf);
    if (msg_end == -1) {
        return 1;
    }

    *dst = malloc(msg_end + 1);
    if (!*dst) {
        perror("malloc");
        exit(1);
    }

    strncpy(*dst, src, msg_end);
    (*dst)[msg_end] = '\0';

    memmove(src, src + msg_end, *inbuf - msg_end);
    *inbuf -= msg_end;

    return 0;
}


int write_to_socket(int sock_fd, char *buf, int len) {
    int bytes_sent = 0;
    while (bytes_sent < len) {
        int ret = send(sock_fd, buf + bytes_sent, len - bytes_sent, 0);
        if (ret == -1) {
            perror("send() failed");
            return 1;
        }
        bytes_sent += ret;
    }
    return 0;
}
