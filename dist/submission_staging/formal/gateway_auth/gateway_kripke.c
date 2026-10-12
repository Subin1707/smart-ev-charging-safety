/*
 * formal/gateway_auth/gateway_kripke.c
 * =====================================================
 * Specialized Kripke Structure for Gateway Authentication
 * =====================================================
 *
 * K = (S, S0, R, L)
 *
 * S  = {WAITING, CONNECTED, AUTH_OK, AUTH_FAIL,
 *       CHARGING, STOPPED, FAULT, EMERGENCY}
 * S0 = WAITING
 * R  = transition relation below
 * L  = labels over C,T,A,R,S,E for each state
 *
 * CHARGING is a system state reached by transition. It is not an independent
 * Gateway Authentication input variable in the state-space enumeration.
 */

#include <stdio.h>

#include "gateway_kripke.h"

static const char *STATE_NAMES[GA_STATE_COUNT] = {
    "WAITING",
    "CONNECTED",
    "AUTH_OK",
    "AUTH_FAIL",
    "CHARGING",
    "STOPPED",
    "FAULT",
    "EMERGENCY",
};

static const GatewayLabel STATE_LABELS[GA_STATE_COUNT] = {
    /* WAITING   */ {0, 0, 0, 0, 1, 0},
    /* CONNECTED */ {1, 0, 0, 0, 1, 0},
    /* AUTH_OK   */ {1, 1, 1, 0, 1, 0},
    /* AUTH_FAIL */ {1, 0, 0, 0, 1, 0},
    /* CHARGING  */ {1, 1, 1, 1, 1, 0},
    /* STOPPED   */ {1, 1, 1, 0, 1, 0},
    /* FAULT     */ {1, 1, 1, 1, 0, 0},
    /* EMERGENCY */ {1, 1, 1, 1, 0, 1},
};

static const int TRANSITIONS[GA_STATE_COUNT][5] = {
    /* WAITING   */ {GA_CONNECTED, -1},
    /* CONNECTED */ {GA_AUTH_FAIL, GA_AUTH_OK, -1},
    /* AUTH_OK   */ {GA_CHARGING, -1},
    /* AUTH_FAIL */ {GA_WAITING, -1},
    /* CHARGING  */ {GA_STOPPED, GA_FAULT, GA_EMERGENCY, -1},
    /* STOPPED   */ {GA_WAITING, -1},
    /* FAULT     */ {GA_WAITING, -1},
    /* EMERGENCY */ {GA_WAITING, -1},
};

const char *gateway_state_name(GatewayState state)
{
    if (state < 0 || state >= GA_STATE_COUNT) {
        return "UNKNOWN";
    }
    return STATE_NAMES[state];
}

GatewayLabel gateway_label(GatewayState state)
{
    GatewayLabel empty = {0, 0, 0, 0, 0, 0};
    if (state < 0 || state >= GA_STATE_COUNT) {
        return empty;
    }
    return STATE_LABELS[state];
}

int gateway_transition_hop_le(GatewayState from, GatewayState to)
{
    if (from < 0 || from >= GA_STATE_COUNT || to < 0 || to >= GA_STATE_COUNT) {
        return 0;
    }

    for (int i = 0; i < 5 && TRANSITIONS[from][i] != -1; i++) {
        if (TRANSITIONS[from][i] == (int)to) {
            return 1;
        }
    }
    return 0;
}

static int label_satisfies_gateway_constraints(GatewayLabel label)
{
    if (label.A && !label.C) {
        return 0;
    }
    if (label.A && !label.T) {
        return 0;
    }
    return 1;
}

static int check_charging_requires_auth(GatewayState state)
{
    GatewayLabel label = gateway_label(state);
    if (state == GA_CHARGING) {
        return label.C && label.T && label.A && label.R && label.S && !label.E;
    }
    return 1;
}

static int check_emergency_blocks_charging(GatewayState state)
{
    GatewayLabel label = gateway_label(state);
    if (label.E) {
        return state != GA_CHARGING;
    }
    return 1;
}

static void print_label(GatewayLabel label)
{
    printf("C=%d T=%d A=%d R=%d S=%d E=%d",
           label.C, label.T, label.A, label.R, label.S, label.E);
}

int main(void)
{
    int visited[GA_STATE_COUNT] = {0};
    GatewayState queue[GA_STATE_COUNT * 5];
    int q_head = 0;
    int q_tail = 0;
    int violations = 0;
    int states_checked = 0;

    printf("=====================================================\n");
    printf("  GATEWAY AUTH KRIPKE MODEL\n");
    printf("  K = (S, S0, R, L) | S0 = WAITING\n");
    printf("=====================================================\n\n");

    queue[q_tail++] = GA_WAITING;
    visited[GA_WAITING] = 1;

    while (q_head < q_tail) {
        GatewayState state = queue[q_head++];
        GatewayLabel label = gateway_label(state);
        states_checked++;

        printf("  %-10s | ", gateway_state_name(state));
        print_label(label);
        printf("\n");

        if (!label_satisfies_gateway_constraints(label)) {
            printf("    [VIOLATION] label violates GA-C01 or GA-C02\n");
            violations++;
        }

        if (!check_charging_requires_auth(state)) {
            printf("    [VIOLATION] CHARGING violates START_ALLOWED labels\n");
            violations++;
        }

        if (!check_emergency_blocks_charging(state)) {
            printf("    [VIOLATION] emergency state is charging\n");
            violations++;
        }

        for (int i = 0; i < 5 && TRANSITIONS[state][i] != -1; i++) {
            GatewayState next = (GatewayState)TRANSITIONS[state][i];
            printf("    -> %-10s\n", gateway_state_name(next));
            if (!visited[next]) {
                visited[next] = 1;
                queue[q_tail++] = next;
            }
        }
    }

    printf("\n=====================================================\n");
    printf("  GATEWAY AUTH KRIPKE RESULTS\n");
    printf("=====================================================\n");
    printf("  States reachable : %d / %d\n", states_checked, GA_STATE_COUNT);
    printf("  Transition witness: WAITING -> CONNECTED -> AUTH_OK -> CHARGING\n");

    if (!gateway_transition_hop_le(GA_WAITING, GA_CONNECTED) ||
        !gateway_transition_hop_le(GA_CONNECTED, GA_AUTH_OK) ||
        !gateway_transition_hop_le(GA_AUTH_OK, GA_CHARGING)) {
        violations++;
    }

    if (violations == 0) {
        printf("  VERDICT: GATEWAY KRIPKE MODEL HOLDS\n");
    } else {
        printf("  VERDICT: %d VIOLATION(S) FOUND\n", violations);
    }
    printf("=====================================================\n");

    return violations == 0 ? 0 : 1;
}
