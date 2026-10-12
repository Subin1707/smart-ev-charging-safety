#include <assert.h>
#include <stdbool.h>

extern bool nondet_bool(void);

int main(void)
{
    bool USER_VERIFICATION = nondet_bool();
    bool ACCOUNT_ACTIVATION = nondet_bool();
    if (ACCOUNT_ACTIVATION) assert(USER_VERIFICATION);
    return 0;
}
