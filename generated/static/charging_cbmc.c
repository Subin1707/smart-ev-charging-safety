/* Generated from specification/charging.json */
#include <assert.h>
#include <stdbool.h>

extern bool nondet_bool(void);
extern int nondet_int(void);

int main(void)
{
    bool C = nondet_bool();
    bool A = nondet_bool();
    bool B = nondet_bool();
    bool T = nondet_bool();
    bool P = nondet_bool();
    bool E = nondet_bool();
    bool F = nondet_bool();

    (void)C;
    (void)A;
    (void)B;
    (void)T;
    (void)P;
    (void)E;
    (void)F;

    assert(C && A && B && T && P && (! E) && (! F)); /* CHG-01 */

    return 0;
}