/* Generated from specification/port.json */
#define assert(e) __CPROVER_assert((e), #e)

extern int nondet_int(void);

int main(void)
{
    int connected = nondet_int() != 0;
    int occupied = nondet_int() != 0;
    int port_charging = nondet_int() != 0;
    int port_fault = nondet_int() != 0;

    assert(!port_charging || connected);   /* PORT-01 */
    assert(!port_charging || occupied);    /* PORT-02 */
    assert(!port_fault || !port_charging); /* PORT-03 */

    return 0;
}
