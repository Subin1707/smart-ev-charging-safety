#include <stdio.h>

typedef struct {
    char command[16];
    char vehicle_id[20];
    int port;
    float power;
} ThongDiepAnToan;

int phan_tich_thong_diep_an_toan(const char *raw_msg, ThongDiepAnToan *msg);

int main(void) {
    unsigned char input[512];
    size_t size = fread(input, 1, sizeof(input) - 1, stdin);
    input[size] = '\0';

    ThongDiepAnToan message = {0};
    int parsed = phan_tich_thong_diep_an_toan((const char *)input, &message);
    printf("parsed=%d\n", parsed);
    printf("safety_violation=%d\n",
           parsed && (message.port < 1 || message.port > 5 || message.power < 0.0f || message.power > 22.0f));
    return 0;
}