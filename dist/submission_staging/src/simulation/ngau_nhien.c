#include <stdlib.h>
#include <time.h>
#include "ngau_nhien.h"

unsigned int khoi_tao_ngau_nhien(unsigned int seed) {
    if (seed == 0) {
        seed = (unsigned int)time(NULL);
    }

    srand(seed);
    return seed;
}

int sinh_so_nguyen_ngau_nhien(int min, int max) {
    if (min >= max) return min;
    return min + rand() % (max - min + 1);
}

float sinh_so_thuc_ngau_nhien(float min, float max) {
    if (min >= max) return min;
    float scale = rand() / (float)RAND_MAX;
    return min + scale * (max - min);
}
