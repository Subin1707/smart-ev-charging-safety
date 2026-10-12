#include <stdio.h>
#include <string.h>
#include <stdlib.h>

typedef struct {
    char command[16];
    char vehicle_id[20];
    int port;
    float power;
} ThongDiepAnToan;

int phan_tich_thong_diep_an_toan(const char *raw_msg, ThongDiepAnToan *msg) {
    if (!raw_msg || !msg) return 0;

    char buffer[128];
    /* FIX: Dung snprintf gioi han buffer kich thuoc du lon */
    snprintf(buffer, sizeof(buffer), "%s", raw_msg);

    char *saveptr = NULL;
    char *token = strtok_r(buffer, "|", &saveptr);
    if (!token) return 0;
    snprintf(msg->command, sizeof(msg->command), "%s", token);

    token = strtok_r(NULL, "|", &saveptr);
    if (!token) return 0;
    snprintf(msg->vehicle_id, sizeof(msg->vehicle_id), "%s", token);

    token = strtok_r(NULL, "|", &saveptr);
    if (!token) return 0;
    msg->port = atoi(token);

    token = strtok_r(NULL, "|", &saveptr);
    if (!token) return 0;
    msg->power = (float)atof(token);

    if (msg->port < 1 || msg->port > 5 || msg->power < 0.0f || msg->power > 22.0f) return 0;

    return 1;
}

int main(void) {
    ThongDiepAnToan msg;
    const char *raw_packet = "START|EV99999999999999999999999999999999999999999999|1|22.0";

    printf("[FIXED] Parsing packet an toan: %s\n", raw_packet);
    if (phan_tich_thong_diep_an_toan(raw_packet, &msg)) {
        printf("[FIXED] Command: %s, Vehicle: %s, Port: %d, Power: %.1f\n",
               msg.command, msg.vehicle_id, msg.port, msg.power);
    }

    return 0;
}
