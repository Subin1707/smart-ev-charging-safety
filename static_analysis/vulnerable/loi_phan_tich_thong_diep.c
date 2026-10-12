#include <stdio.h>
#include <string.h>
#include <stdlib.h>

/* VULN-02: Unsafe message parser
   Dung strtok va sprintf khong gioi han bo dem */
typedef struct {
    char command[16];
    char vehicle_id[20];
    int port;
    float power;
} ThongDiepLoi;

void phan_tich_thong_diep_nguy_hiem(const char *raw_msg, ThongDiepLoi *msg) {
    char buffer[32];
    /* NGUY HIEM: sprintf khong an toan, buffer de bi tran */
    sprintf(buffer, "%s", raw_msg);

    char *token = strtok(buffer, "|");
    if (token) strcpy(msg->command, token);

    token = strtok(NULL, "|");
    if (token) strcpy(msg->vehicle_id, token);

    token = strtok(NULL, "|");
    if (token) msg->port = atoi(token);

    token = strtok(NULL, "|");
    if (token) msg->power = (float)atof(token);
}

int main(void) {
    ThongDiepLoi msg;
    const char *raw_packet = "START|EV99999999999999999999999999999999999999999999|1|22.0";

    printf("[VULNERABLE] Parsing packet: %s\n", raw_packet);
    phan_tich_thong_diep_nguy_hiem(raw_packet, &msg);
    printf("[VULNERABLE] Command: %s, Vehicle: %s, Port: %d\n", msg.command, msg.vehicle_id, msg.port);

    return 0;
}
