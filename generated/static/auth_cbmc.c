/* Generated from specification/auth.json */
#include <assert.h>
#include <stdbool.h>

extern bool nondet_bool(void);
extern int nondet_int(void);

int main(void)
{
    bool C = nondet_bool();
    bool T = nondet_bool();
    bool A = nondet_bool();
    bool X = nondet_bool();
    bool A_after_disconnect = nondet_bool();

    (void)C;
    (void)T;
    (void)A;
    (void)X;
    (void)A_after_disconnect;

    assert((! A) || C); /* AUTH-01 */
    assert((! A) || T); /* AUTH-02 */
    assert(C || (! A)); /* AUTH-03 */
    assert((! X) || (! A_after_disconnect)); /* AUTH-04 */

    return 0;
}