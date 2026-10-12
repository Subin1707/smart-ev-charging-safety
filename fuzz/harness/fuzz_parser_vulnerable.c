#include <stdio.h>
#include <stdlib.h>

typedef struct {
    char command[16];
    char vehicle_id[20];
    int port;
    float power;
} ThongDiepLoi;

void phan_tich_thong_diep_nguy_hiem(const char *raw_msg, ThongDiepLoi *msg);

int main(void) {
    unsigned char input[512];
    size_t size = fread(input, 1, sizeof(input) - 1, stdin);
    input[size] = '\0';

    ThongDiepLoi message = {0};
    phan_tich_thong_diep_nguy_hiem((const char *)input, &message);
    printf("parsed=1\n");
    printf("safety_violation=%d\n",
           message.port < 1 || message.port > 5 || message.power < 0.0f || message.power > 22.0f);
    return 0;
}