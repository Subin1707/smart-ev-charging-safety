#include <assert.h>

int main(void) {
    int soc;
    int charging;

    __CPROVER_assume(soc >= 0 && soc <= 101);

    /* Vulnerable: full batteries are still allowed to charge. */
    charging = 1;

    assert(soc < 100 || !charging);
    return 0;
}
