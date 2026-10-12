#include <assert.h>

int main(void) {
    int overheat;
    int charging;

    __CPROVER_assume(overheat == 0 || overheat == 1);

    /* Vulnerable: overheating does not cut charging power. */
    charging = 1;

    assert(!overheat || !charging);
    return 0;
}
