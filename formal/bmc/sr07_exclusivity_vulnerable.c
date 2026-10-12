#include <assert.h>

int main(void) {
    int first_vehicle;
    int second_vehicle;
    int port_vehicle = 0;

    __CPROVER_assume(first_vehicle >= 1 && first_vehicle <= 5);
    __CPROVER_assume(second_vehicle >= 1 && second_vehicle <= 5);
    __CPROVER_assume(first_vehicle != second_vehicle);

    port_vehicle = first_vehicle;
    /* Vulnerable: a second vehicle silently replaces the first. */
    port_vehicle = second_vehicle;

    assert(port_vehicle == first_vehicle);
    return 0;
}
