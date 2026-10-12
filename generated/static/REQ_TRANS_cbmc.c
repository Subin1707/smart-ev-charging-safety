#include <assert.h>

typedef enum {
    ENUM_UNKNOWN = 0,
    IDLE,
    RUNNING
} GeneratedState;

int valid_transition(GeneratedState from, GeneratedState to)
{
    if (from == IDLE && to == RUNNING) return 1;
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
