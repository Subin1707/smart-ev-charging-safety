#include <assert.h>

typedef enum {
    ENUM_UNKNOWN = 0,
    CREATED,
    PAID,
    SHIPPED,
    DELIVERED
} GeneratedState;

int valid_transition(GeneratedState from, GeneratedState to)
{
    if (from == CREATED && to == PAID) return 1;
    if (from == PAID && to == SHIPPED) return 1;
    if (from == SHIPPED && to == DELIVERED) return 1;
    return 0;
}

int main(void)
{
    GeneratedState from = ENUM_UNKNOWN;
    GeneratedState to = ENUM_UNKNOWN;
    (void)from;
    (void)to;
    return 0;
}
