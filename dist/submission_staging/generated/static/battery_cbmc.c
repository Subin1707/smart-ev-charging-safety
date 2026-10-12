/* Generated from specification/battery.json */
#include <assert.h>
#include <stdbool.h>

extern bool nondet_bool(void);
extern int nondet_int(void);

enum SOC { SOC_INVALID, SOC_OK, SOC_FULL };
enum TEMP { TEMP_INVALID, TEMP_SAFE, TEMP_OVERHEAT };

int main(void)
{
    enum SOC SOC = nondet_int();
    __CPROVER_assume(SOC >= 0 && SOC < 3);
    enum TEMP TEMP = nondet_int();
    __CPROVER_assume(TEMP >= 0 && TEMP < 3);

    (void)SOC;
    (void)TEMP;

    assert(SOC != SOC_INVALID); /* BAT-01 */
    assert(SOC != SOC_FULL); /* BAT-02 */
    assert(TEMP != TEMP_OVERHEAT); /* BAT-03 */
    assert(SOC != SOC_INVALID); /* BAT-04 */
    assert(TEMP != TEMP_INVALID); /* BAT-05 */

    return 0;
}