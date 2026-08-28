#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <errno.h>
#include <signal.h>
#include <assert.h>

#include "socket.h"
#include "chat_helpers.h"

int sigint_received = 0;

void sigint_handler(int code) {
    (void)code;
    sigint_received = 1;
}

int accept_connection(int fd, struct client_sock **clients) {
    struct sockaddr_in peer;
    unsigned int peer_len = sizeof(peer);
    peer.sin_family = AF_INET;

    int client_fd = accept(fd, (struct sockaddr *)&peer, &peer_len);
    if (client_fd < 0) {
        perror("server: accept");
        return -1;
    }

    if (client_fd >= MAX_CONNECTIONS) {
        close(client_fd);
        return -1;
    }

    struct client_sock *newclient = malloc(sizeof(struct client_sock));
    if (!newclient) {
        perror("malloc");
        close(client_fd);
        return -1;
    }

    newclient->sock_fd = client_fd;
    newclient->inbuf = newclient->state = 0;
    newclient->username = NULL;
    newclient->next = NULL;
    memset(newclient->buf, 0, BUF_SIZE);

    if (*clients == NULL) {
        *clients = newclient;
    } else {
        struct client_sock *curr = *clients;
        while (curr->next) {
            curr = curr->next;
        }
        curr->next = newclient;
    }

    return client_fd;
}

void clean_exit(struct listen_sock s, struct client_sock *clients, int exit_status) {
    struct client_sock *tmp;
    while (clients) {
        tmp = clients;
        close(tmp->sock_fd);
        clients = clients->next;
        if (tmp->username) free(tmp->username);
        free(tmp);
    }
    close(s.sock_fd);
    free(s.addr);
    exit(exit_status);
}

int run_server(int port) {
    setbuf(stdout, NULL);

    if (signal(SIGPIPE, SIG_IGN) == SIG_ERR) {
        perror("signal");
        exit(1);
    }

    struct client_sock *clients = NULL;

    struct listen_sock s;
    setup_server_socket(&s, port);

    struct sigaction sa_sigint;
    memset (&sa_sigint, 0, sizeof (sa_sigint));
    sa_sigint.sa_handler = sigint_handler;
    sa_sigint.sa_flags = 0;
    sigemptyset(&sa_sigint.sa_mask);
    sigaction(SIGINT, &sa_sigint, NULL);

    int max_fd = s.sock_fd;

    fd_set all_fds, listen_fds;

    FD_ZERO(&all_fds);
    FD_SET(s.sock_fd, &all_fds);

    do {
        listen_fds = all_fds;
        int nready = select(max_fd + 1, &listen_fds, NULL, NULL, NULL);
        if (sigint_received) break;
        if (nready == -1) {
            if (errno == EINTR) continue;
            perror("server: select");
            clean_exit(s, clients, 1);
            return 1;
        }

        if (FD_ISSET(s.sock_fd, &listen_fds)) {
            int client_fd = accept_connection(s.sock_fd, &clients);
            if (client_fd < 0) {
                printf("Failed to accept incoming connection.\n");
                continue;
            }
            if (client_fd > max_fd) {
                max_fd = client_fd;
            }
            FD_SET(client_fd, &all_fds);
            printf("Accepted connection\n");
        }

        if (sigint_received) break;

        struct client_sock *curr = clients;
        while (curr) {
            if (!FD_ISSET(curr->sock_fd, &listen_fds)) {
                curr = curr->next;
                continue;
            }
            int client_closed = read_from_client(curr);

            if (client_closed == -1) {
                client_closed = 1;
            }

            if (client_closed == 0 && curr->username == NULL) {
                if (set_username(curr)) {
                    printf("Error processing user name from client %d.\n", curr->sock_fd);
                    client_closed = 1;
                }
                else {
                    printf("Client %d user name is %s.\n", curr->sock_fd, curr->username);
                }
            }

            char *msg;
            while (client_closed == 0 && !get_message(&msg, curr->buf, &(curr->inbuf))) {
                printf("Echoing message from %s.\n", curr->username);
                char write_buf[BUF_SIZE];
                write_buf[0] = '\0';
                strncat(write_buf, msg, MAX_USER_MSG);
                free(msg);
                int data_len = strlen(write_buf);

                printf("%s\n", write_buf);

                struct client_sock *dest_c = clients;
                while (dest_c) {
                    if (dest_c != curr) {
                        int ret = write_buf_to_client(dest_c, write_buf, data_len);
                        if (ret == 0) {
                            printf("Sent message from %s (%d) to %s (%d).\n",
                                curr->username, curr->sock_fd,
                                dest_c->username, dest_c->sock_fd);
                        }
                        else {
                            printf("Failed to send message to user %s (%d).\n", dest_c->username, dest_c->sock_fd);
                            if (ret == 2) {
                                printf("User %s (%d) disconnected.\n", dest_c->username, dest_c->sock_fd);
                                close(dest_c->sock_fd);
                                FD_CLR(dest_c->sock_fd, &all_fds);
                                assert(remove_client(&dest_c, &clients) == 0);
                                continue;
                            }
                        }
                    }
                    dest_c = dest_c->next;
                }
            }

            if (client_closed == 1) {
                FD_CLR(curr->sock_fd, &all_fds);
                close(curr->sock_fd);
                printf("Client %d disconnected\n", curr->sock_fd);
                assert(remove_client(&curr, &clients) == 0);
            }
            else {
                curr = curr->next;
            }
        }
    } while(!sigint_received);

    clean_exit(s, clients, 0);
    return 0;
}