/* Generated from specification/port.json */
#include <assert.h>
#include <stdbool.h>

extern bool nondet_bool(void);
extern int nondet_int(void);

int main(void)
{
    bool C = nondet_bool();
    bool O = nondet_bool();
    bool P = nondet_bool();
    bool F = nondet_bool();

    (void)C;
    (void)O;
    (void)P;
    (void)F;

    assert((! P) || C); /* PORT-01 */
    assert((! P) || O); /* PORT-02 */
    assert((! F) || (! P)); /* PORT-03 */

    return 0;
}