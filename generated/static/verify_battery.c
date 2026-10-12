/* Generated from specification/battery.json */
#define assert(e) __CPROVER_assert((e), #e)

extern float nondet_float(void);
extern int nondet_int(void);

int main(void)
{
    float soc = nondet_float();
    float temperature = nondet_float();
    int charging = nondet_int() != 0;

    if (charging) {
        assert(soc >= 0.0f && soc < 100.0f);       /* BAT-01/BAT-02/BAT-04 */
        assert(temperature < 60.0f);               /* BAT-03/BAT-05 */
    }

    return 0;
}
