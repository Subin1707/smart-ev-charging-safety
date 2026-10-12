/* Generated from specification/charging.json */
#define assert(e) __CPROVER_assert((e), #e)

extern int nondet_int(void);

int main(void)
{
    int connected = nondet_int() != 0;
    int authenticated = nondet_int() != 0;
    int battery_valid = nondet_int() != 0;
    int temperature_safe = nondet_int() != 0;
    int port_valid = nondet_int() != 0;
    int emergency = nondet_int() != 0;
    int fault = nondet_int() != 0;
    int charging = nondet_int() != 0;

    if (charging) {
        assert(connected && authenticated && battery_valid &&
               temperature_safe && port_valid && !emergency && !fault); /* CHG-01 */
    }

    return 0;
}
