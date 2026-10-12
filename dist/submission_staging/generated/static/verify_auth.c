/* Generated from specification/auth.json */
#define assert(e) __CPROVER_assert((e), #e)

extern int nondet_int(void);

int main(void)
{
    int connected = nondet_int() != 0;
    int token_valid = nondet_int() != 0;
    int authenticated = nondet_int() != 0;
    int disconnect_request = nondet_int() != 0;
    int authenticated_after_disconnect = nondet_int() != 0;

    assert(!authenticated || connected);              /* AUTH-01 */
    assert(!authenticated || token_valid);            /* AUTH-02 */
    assert(connected || !authenticated);              /* AUTH-03 */
    assert(!disconnect_request || !authenticated_after_disconnect); /* AUTH-04 */

    return 0;
}
