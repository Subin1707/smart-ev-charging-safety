#include <assert.h>

int main(void) {
    int requested_kw[5] = {22, 22, 22, 22, 22};
    int allocated_kw[5];
    int total = 0;

    /* Vulnerable: every request is granted independently. */
    for (int i = 0; i < 5; i++) {
        allocated_kw[i] = requested_kw[i];
        total += allocated_kw[i];
    }

    assert(total <= 100);
    return 0;
}
