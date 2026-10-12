#include <stdio.h>
#include <string.h>
#include "token.h"

void sinh_token_xe(const char *ma_xe, char *token_out, int max_len) {
    if (!ma_xe || !token_out || max_len <= 0) return;

    snprintf(token_out, max_len, "TOKEN_%s", ma_xe);
}

int kiem_tra_token_hop_le(const char *ma_xe, const char *token) {
    if (!ma_xe || !token) return 0;

    char token_chuan[DO_DAI_TOKEN];
    sinh_token_xe(ma_xe, token_chuan, sizeof(token_chuan));

    return (strcmp(token, token_chuan) == 0);
}
