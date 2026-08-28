#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/select.h>

#include "socket.h"

struct server_sock {
    int sock_fd;
    char buf[BUF_SIZE];
    int inbuf;
};

int run_client(const char *hostname, int port) {
    struct server_sock s;
    s.inbuf = 0;
    int exit_status = 0;

    s.sock_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (s.sock_fd < 0) {
        perror("client: socket");
        exit(1);
    }

    struct sockaddr_in server;
    server.sin_family = AF_INET;
    server.sin_port = htons(port);
    if (inet_pton(AF_INET, hostname, &server.sin_addr) < 1) {
        perror("client: inet_pton");
        close(s.sock_fd);
        exit(1);
    }

    if (connect(s.sock_fd, (struct sockaddr *)&server, sizeof(server)) == -1) {
        perror("client: connect");
        close(s.sock_fd);
        exit(1);
    }

    char *buf = NULL;
    int name_valid = 0;
    while(!name_valid) {
        printf("Please enter a username: ");
        fflush(stdout);
        size_t buf_len = 0;
        ssize_t name_len = getline(&buf, &buf_len, stdin);
        if (name_len < 0) {
            perror("getline");
            fprintf(stderr, "Error reading username.\n");
            free(buf);
            exit(1);
        }

        if (name_len - 1 > MAX_NAME) {
            printf("Username can be at most %d characters.\n", MAX_NAME);
        }
        else {
            buf[name_len-1] = '\r';
            buf[name_len] = '\n';
            if (write_to_socket(s.sock_fd, buf, name_len+1)) {
                fprintf(stderr, "Error sending username.\n");
                free(buf);
                exit(1);
            }
            name_valid = 1;
            free(buf);
        }
    }

    fd_set read_fds;
    char stdin_buf[MAX_USER_MSG + 3];

    while(1) {
        FD_ZERO(&read_fds);
        FD_SET(STDIN_FILENO, &read_fds);
        FD_SET(s.sock_fd, &read_fds);
        int max_fd = (s.sock_fd > STDIN_FILENO) ? s.sock_fd : STDIN_FILENO;

        int nready = select(max_fd + 1, &read_fds, NULL, NULL, NULL);
        if (nready == -1) {
            perror("client: select");
            exit_status = 1;
            break;
        }

        if (FD_ISSET(STDIN_FILENO, &read_fds)) {
            memset(stdin_buf, 0, sizeof(stdin_buf));

            if (fgets(stdin_buf, MAX_USER_MSG + 1, stdin) == NULL) {
                if (feof(stdin)) {
                    printf("EOF received. Exiting.\n");
                    break;
                } else {
                    perror("client: fgets");
                    exit_status = 1;
                    break;
                }
            }

            int invalid = 0;
            size_t len = strlen(stdin_buf);
            for (size_t i = 0; i < len; i++) {
                if ((stdin_buf[i] == '\r' || stdin_buf[i] == '\n') && i != len - 1) {
                    invalid = 1;
                    break;
                }
            }

            if (invalid) {
                fprintf(stderr, "Message contains invalid characters (CR/LF).\n");
                int c;
                while ((c = getchar()) != '\n' && c != EOF);
                continue;
            }

            if (len > 0 && stdin_buf[len - 1] == '\n') {
                stdin_buf[len - 1] = '\r';
                stdin_buf[len] = '\n';
                stdin_buf[len + 1] = '\0';
                len += 1;
            } else {
                if (len >= MAX_USER_MSG) {
                    ungetc(stdin_buf[len - 1], stdin);
                    len--;
                }
                stdin_buf[len] = '\r';
                stdin_buf[len + 1] = '\n';
                len += 2;
            }

            fflush(stdout);

            if (write_to_socket(s.sock_fd, stdin_buf, len) != 0) {
                fprintf(stderr, "Error sending message.\n");
                exit_status = 1;
                break;
            }
        }

        if (FD_ISSET(s.sock_fd, &read_fds)) {
            int ret = read_from_socket(s.sock_fd, s.buf, &s.inbuf);
            if (ret == 1) {
                printf("Server closed connection.\n");
                break;
            } else if (ret == -1) {
                perror("client: read_from_socket");
                exit_status = 1;
                break;
            }

            char *msg = NULL;
            while (get_message(&msg, s.buf, &s.inbuf) == 0) {

                char *space = strchr(msg, ' ');
                if (!space) {
                    fprintf(stderr, "Invalid server message format.\n");
                    free(msg);
                    continue;
                }

                *space = '\0';
                char *username = msg;
                char *user_msg = space + 1;

                char *crlf = strstr(user_msg, "\r\n");
                if (crlf) *crlf = '\0';

                printf("%s: %s\n", username, user_msg);
                fflush(stdout);
                free(msg);
            }
        }
    }

    close(s.sock_fd);
    exit(exit_status);
}