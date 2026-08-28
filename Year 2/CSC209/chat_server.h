#ifndef CHAT_SERVER_H
#define CHAT_SERVER_H

#include "socket.h"
#include "chat_helpers.h"

void run_chat_server(struct listen_sock *s, struct client_sock **clients);
int run_server(int port);

#endif