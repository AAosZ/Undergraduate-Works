#ifndef __VARIABLES_H__
#define __VARIABLES_H__

#include <stddef.h>

typedef struct VarNode {
    char *name;
    char *value;
    struct VarNode *next;
} VarNode;

void set_variable(const char *name, const char *value);
char *get_variable(const char *name);
void expansion(char *input);
void free_variables(void);

#endif
