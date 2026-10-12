#ifndef GATEWAY_KRIPKE_H
#define GATEWAY_KRIPKE_H

typedef enum {
    GA_WAITING,
    GA_CONNECTED,
    GA_AUTH_OK,
    GA_AUTH_FAIL,
    GA_CHARGING,
    GA_STOPPED,
    GA_FAULT,
    GA_EMERGENCY,
    GA_STATE_COUNT
} GatewayState;

typedef struct {
    int C; /* Connected */
    int T; /* Token Valid */
    int A; /* Authenticated */
    int R; /* Start Request */
    int S; /* Safety OK */
    int E; /* Emergency */
} GatewayLabel;

const char *gateway_state_name(GatewayState state);
GatewayLabel gateway_label(GatewayState state);
int gateway_transition_hop_le(GatewayState from, GatewayState to);

#endif
