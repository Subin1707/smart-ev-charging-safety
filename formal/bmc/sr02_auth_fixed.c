#include <assert.h>

int main(void) {
    int connected;
    int authenticated;
    int charging;

    __CPROVER_assume(connected == 0 || connected == 1);
    __CPROVER_assume(authenticated == 0 || authenticated == 1);

    /* Fixed: authentication is required before charging. */
    charging = connected && authenticated;

    assert(!charging || authenticated);
    return 0;
}
