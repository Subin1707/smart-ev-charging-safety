#ifndef KRIPKE_SAC_H
#define KRIPKE_SAC_H
typedef enum {
    S_WAITING, S_CONNECTED, S_AUTH_OK, S_AUTH_FAIL, S_CHARGING,
    S_FAULT, S_EMERGENCY, S_STOPPED, S_COUNT
} State;
int transition_hop_le(State from, State to);
#endif
