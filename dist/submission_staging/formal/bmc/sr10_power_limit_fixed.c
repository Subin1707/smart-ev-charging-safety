#include <assert.h>

int main(void) {
    int requested_kw[5] = {22, 22, 22, 22, 22};
    int allocated_kw[5];
    int total_requested = 0;
    int total_allocated = 0;

    for (int i = 0; i < 5; i++) {
        total_requested += requested_kw[i];
    }

    /* Fixed: power manager caps the aggregate allocation at 100 kW. */
    if (total_requested > 100) {
        int remaining = 100;
        for (int i = 0; i < 5; i++) {
            allocated_kw[i] = requested_kw[i] < remaining ? requested_kw[i] : remaining;
            remaining -= allocated_kw[i];
            total_allocated += allocated_kw[i];
        }
    } else {
        for (int i = 0; i < 5; i++) {
            allocated_kw[i] = requested_kw[i];
            total_allocated += allocated_kw[i];
        }
    }

    assert(total_allocated <= 100);
    return 0;
}
