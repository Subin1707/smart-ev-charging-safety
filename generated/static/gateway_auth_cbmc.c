/* Generated Gateway Auth aggregate CBMC harness. */
#define assert(e) __CPROVER_assert((e), #e)

extern unsigned int nondet_uint(void);

int main(void)
{
    unsigned int state = nondet_uint();
    __CPROVER_assume(state < 8);

    int connected = 0;
    int token_valid = 0;
    int authenticated = 0;
    int start_request = 0;
    int safety_ok = 0;
    int emergency = 0;
    int charging = 0;
    int start_allowed = 0;

    switch (state) {
    case 0: /* WAITING */
        safety_ok = 1;
        break;
    case 1: /* CONNECTED */
        connected = 1;
        safety_ok = 1;
        break;
    case 2: /* AUTH_OK */
        connected = 1;
        token_valid = 1;
        authenticated = 1;
        safety_ok = 1;
        break;
    case 3: /* AUTH_FAIL */
        connected = 1;
        safety_ok = 1;
        break;
    case 4: /* CHARGING */
        connected = 1;
        token_valid = 1;
        authenticated = 1;
        start_request = 1;
        safety_ok = 1;
        charging = 1;
        start_allowed = 1;
        break;
    case 5: /* STOPPED */
        connected = 1;
        token_valid = 1;
        authenticated = 1;
        safety_ok = 1;
        break;
    case 6: /* FAULT */
        connected = 1;
        token_valid = 1;
        authenticated = 1;
        start_request = 1;
        break;
    case 7: /* EMERGENCY */
        connected = 1;
        token_valid = 1;
        authenticated = 1;
        start_request = 1;
        emergency = 1;
        break;
    }

    assert(!authenticated || connected); /* GA-C01 */
    assert(!authenticated || token_valid); /* GA-C02 */
    assert(!charging || connected); /* GA-C03 */
    assert(!charging || authenticated); /* GA-C04 */
    assert(!charging || safety_ok); /* GA-C05 */
    assert(!emergency || !charging); /* GA-C06 */
    assert(connected || !authenticated); /* GA-C07 */
    assert(!start_allowed || (connected && token_valid && authenticated && start_request && safety_ok && !emergency)); /* GA-C08 */

    return 0;
}
