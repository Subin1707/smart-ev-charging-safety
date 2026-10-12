#include <assert.h>

int main(void) {
    int overheat;
    int charging;

    __CPROVER_assume(overheat == 0 || overheat == 1);

    /* Fixed: an overheated battery cannot remain charging. */
    charging = !overheat;

    assert(!overheat || !charging);
    return 0;
}
