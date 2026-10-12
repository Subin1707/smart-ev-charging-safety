#include <assert.h>

int main(void) {
    int emergency;
    int power_kw = 22;

    __CPROVER_assume(emergency == 0 || emergency == 1);

    /* Vulnerable: emergency state is recorded but power is not cut. */
    if (emergency) {
        power_kw = power_kw;
    }

    assert(!emergency || power_kw == 0);
    return 0;
}
