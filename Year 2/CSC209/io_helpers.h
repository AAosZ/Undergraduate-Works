#ifndef __IO_HELPERS_H__
#define __IO_HELPERS_H__

#include <sys/types.h>


#define MAX_STR_LEN 128
#define DELIMITERS " \t\n"
void display_message(char *str);
void display_error(char *pre_str, char *str);

ssize_t get_input(char *in_ptr);

size_t tokenize_input(char *in_ptr, char **tokens);


#endif
