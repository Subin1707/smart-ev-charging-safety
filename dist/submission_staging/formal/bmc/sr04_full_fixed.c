#include <assert.h>

int main(void) {
    int soc;
    int charging;

    __CPROVER_assume(soc >= 0 && soc <= 101);

    /* Fixed: charging stops at full SOC. */
    charging = soc < 100;

    assert(soc < 100 || !charging);
    return 0;
}
