#include <assert.h>

int main(void) {
    int emergency;
    int power_kw = 22;

    __CPROVER_assume(emergency == 0 || emergency == 1);

    /* Fixed: emergency always cuts port power. */
    if (emergency) {
        power_kw = 0;
    }

    assert(!emergency || power_kw == 0);
    return 0;
}
