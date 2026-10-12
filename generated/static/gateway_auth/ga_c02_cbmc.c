/* Generated Gateway Auth CBMC harness.
 * Source constraint: GA-C02
 * Meaning: Authenticated implies Token Valid
 */
#include <assert.h>
#include <stdbool.h>

extern bool nondet_bool(void);

int main(void)
{
    bool connected = nondet_bool();
    bool token_valid = nondet_bool();
    bool authenticated = nondet_bool();
    bool start_request = nondet_bool();
    bool safety_ok = nondet_bool();
    bool emergency = nondet_bool();
    bool charging = nondet_bool();

    (void)connected;
    (void)token_valid;
    (void)authenticated;
    (void)start_request;
    (void)safety_ok;
    (void)emergency;
    (void)charging;

    assert(!authenticated || token_valid);

    return 0;
}
