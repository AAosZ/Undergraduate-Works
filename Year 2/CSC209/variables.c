#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>
#include "variables.h"
#include "io_helpers.h"

static VarNode *head = NULL;

void set_variable(const char *name, const char *value) {
    VarNode *current = head;

    while (current) {
        if (strcmp(current->name, name) == 0) {
            free(current->value);
            current->value = strdup(value);
            return;
        }
        current = current->next;
    }

    VarNode *new_var = malloc(sizeof(VarNode));
    if (!new_var) {
        fprintf(stderr, "ERROR: Memory allocation failed\n");
        return;
    }

    new_var->name = strdup(name);
    new_var->value = strdup(value);
    new_var->next = head;
    head = new_var;
}

char *get_variable(const char *name) {
    VarNode *current = head;
    while (current) {
        if (strcmp(current->name, name) == 0) {
            return current->value;
        }
        current = current->next;
    }
    return "";
}

void expansion(char *input) {
    char expanded[MAX_STR_LEN] = {0};
    char *src = input, *dest = expanded;
    char var_name[MAX_STR_LEN] = {0};

    while (*src && (dest - expanded) < MAX_STR_LEN - 1) {
        if (*src == '$') {
            src++;
            memset(var_name, 0, MAX_STR_LEN);
            int i = 0;

            while (*src && (isalnum(*src) || *src == '_') && i < MAX_STR_LEN - 1) {
                var_name[i++] = *src++;
            }
            var_name[i] = '\0';

            char *value = get_variable(var_name);

            size_t remaining = MAX_STR_LEN - strlen(expanded) - 1;
            if (strlen(value) < remaining) {
                strncat(dest, value, remaining);
                dest += strlen(value);
            }
        } else {
            if ((dest - expanded) < MAX_STR_LEN - 1) {
                *dest++ = *src++;
            } else {
                break;
            }
        }
    }
    *dest = '\0';
    strncpy(input, expanded, MAX_STR_LEN);
}

void free_variables() {
    VarNode *current = head;
    while (current) {
        VarNode *temp = current;
        current = current->next;
        free(temp->name);
        free(temp->value);
        free(temp);
    }
    head = NULL;
}
