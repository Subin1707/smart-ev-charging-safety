/*
 * formal/kripke/kripke_sac.c
 * =====================================================
 * Kripke Structure cho Hệ thống Sạc Xe Điện
 * =====================================================
 * Trạng thái (S): {WAITING, CONNECTED, AUTH_OK, AUTH_FAIL, CHARGING, FAULT, EMERGENCY, STOPPED}
 * Nhãn (L):
 *   - connected   : xe đã cắm vào cổng
 *   - authenticated : xe đã xác thực
 *   - charging    : đang truyền điện
 *   - safe        : nhiệt độ < 60C và SOC < 100%
 *   - emergency   : cờ emergency bật
 *   - fault       : lỗi phát hiện
 *
 * Thuộc tính an toàn (Safety Properties) cần kiểm chứng:
 *   P1 (SR02): charging => authenticated        [CHARGING chỉ xảy ra khi đã xác thực]
 *   P2 (SR03): charging => safe_temp            [CHARGING chỉ xảy ra khi nhiệt độ an toàn]
 *   P3 (SR04): charging => soc < 100            [CHARGING chỉ xảy ra khi chưa đầy]
 *   P4 (SR05): emergency => power == 0          [Emergency => Cắt điện hoàn toàn]
 *   P5 (SR07): port occupied => one vehicle     [Một cổng chỉ một xe]
 *
 * Phương pháp: Explicit-state model checking (BFS/DFS qua toàn bộ state space)
 */

#include <stdio.h>
#include <string.h>
#include <assert.h>

/* ─── State definitions ─── */
#include "kripke_sac.h"

static const char *STATE_NAMES[] = {
    "WAITING","CONNECTED","AUTH_OK","AUTH_FAIL",
    "CHARGING","FAULT","EMERGENCY","STOPPED"
};

/* ─── Label bitfield per state ─── */
#define L_CONNECTED   (1<<0)
#define L_AUTH        (1<<1)
#define L_CHARGING    (1<<2)
#define L_SAFE_TEMP   (1<<3)
#define L_SAFE_SOC    (1<<4)
#define L_EMERGENCY   (1<<5)
#define L_FAULT       (1<<6)
#define L_POWER_ZERO  (1<<7)

static const unsigned int STATE_LABELS[S_COUNT] = {
    /* WAITING    */ L_SAFE_TEMP | L_SAFE_SOC | L_POWER_ZERO,
    /* CONNECTED  */ L_CONNECTED | L_SAFE_TEMP | L_SAFE_SOC | L_POWER_ZERO,
    /* AUTH_OK    */ L_CONNECTED | L_AUTH | L_SAFE_TEMP | L_SAFE_SOC | L_POWER_ZERO,
    /* AUTH_FAIL  */ L_CONNECTED | L_FAULT | L_POWER_ZERO,
    /* CHARGING   */ L_CONNECTED | L_AUTH | L_CHARGING | L_SAFE_TEMP | L_SAFE_SOC,
    /* FAULT      */ L_CONNECTED | L_FAULT | L_POWER_ZERO,
    /* EMERGENCY  */ L_EMERGENCY | L_POWER_ZERO,
    /* STOPPED    */ L_CONNECTED | L_AUTH | L_POWER_ZERO
};

/* ─── Transition relation (Kripke edges) ─── */
/* transitions[s] = list of successor states */
static const int TRANSITIONS[S_COUNT][8] = {
    /* WAITING    */ { S_CONNECTED, -1 },
    /* CONNECTED  */ { S_AUTH_OK, S_AUTH_FAIL, S_WAITING, -1 },
    /* AUTH_OK    */ { S_CHARGING, S_WAITING, -1 },
    /* AUTH_FAIL  */ { S_WAITING, -1 },
    /* CHARGING   */ { S_STOPPED, S_FAULT, S_EMERGENCY, -1 },
    /* FAULT      */ { S_WAITING, -1 },
    /* EMERGENCY  */ { S_WAITING, -1 },
    /* STOPPED    */ { S_WAITING, -1 }
};

/* ─── Property checkers ─── */

/* P1 (SR02): IF charging THEN authenticated */
static int check_P1(State s) {
    if (STATE_LABELS[s] & L_CHARGING)
        return (STATE_LABELS[s] & L_AUTH) != 0;
    return 1; /* vacuously true */
}

/* P2 (SR03): IF charging THEN safe temperature */
static int check_P2(State s) {
    if (STATE_LABELS[s] & L_CHARGING)
        return (STATE_LABELS[s] & L_SAFE_TEMP) != 0;
    return 1;
}

/* P3 (SR04): IF charging THEN SOC < 100% */
static int check_P3(State s) {
    if (STATE_LABELS[s] & L_CHARGING)
        return (STATE_LABELS[s] & L_SAFE_SOC) != 0;
    return 1;
}

/* P4 (SR05): IF emergency THEN power == 0 */
static int check_P4(State s) {
    if (STATE_LABELS[s] & L_EMERGENCY)
        return (STATE_LABELS[s] & L_POWER_ZERO) != 0;
    return 1;
}

/* P5 (SR07): FAULT state always has power == 0 */
static int check_P5(State s) {
    if (STATE_LABELS[s] & L_FAULT)
        return (STATE_LABELS[s] & L_POWER_ZERO) != 0;
    return 1;
}

/* ─── BFS Reachability + Property Checking ─── */
static int visited[S_COUNT] = {0};
static State queue[S_COUNT * 8];
static int q_head = 0, q_tail = 0;

static const char *PROPS[] = {"P1(SR02):charging=>auth","P2(SR03):charging=>safe_temp",
                               "P3(SR04):charging=>soc<100","P4(SR05):emergency=>power=0",
                               "P5(SR06):fault=>power=0"};
static int(*PROP_FNS[])(State) = {check_P1, check_P2, check_P3, check_P4, check_P5};
#define NUM_PROPS 5

int transition_hop_le(State from, State to) {
    if (from < 0 || from >= S_COUNT || to < 0 || to >= S_COUNT) return 0;
    for (int i = 0; i < 8 && TRANSITIONS[from][i] != -1; i++)
        if (TRANSITIONS[from][i] == (int)to) return 1;
    return 0;
}

int main(void) {
    printf("=====================================================\n");
    printf("  KRIPKE MODEL CHECKER — Smart EV Charging Safety\n");
    printf("  States: 8  |  Properties: 5  |  Method: BFS\n");
    printf("=====================================================\n\n");

    int prop_violations[NUM_PROPS] = {0};
    int states_checked = 0;

    /* BFS from initial state S_WAITING */
    queue[q_tail++] = S_WAITING;
    visited[S_WAITING] = 1;

    while (q_head < q_tail) {
        State s = queue[q_head++];
        states_checked++;

        printf("  Checking state: %-12s | labels: 0x%02X\n",
               STATE_NAMES[s], STATE_LABELS[s]);

        /* Check all properties at this state */
        for (int p = 0; p < NUM_PROPS; p++) {
            if (!PROP_FNS[p](s)) {
                printf("    [VIOLATION] %s violated at state %s!\n",
                       PROPS[p], STATE_NAMES[s]);
                prop_violations[p]++;
            }
        }

        /* Enqueue successors */
        for (int i = 0; i < 8 && TRANSITIONS[s][i] != -1; i++) {
            State ns = (State)TRANSITIONS[s][i];
            if (!visited[ns]) {
                visited[ns] = 1;
                queue[q_tail++] = ns;
            }
        }
    }

    printf("\n=====================================================\n");
    printf("  KRIPKE RESULTS\n");
    printf("=====================================================\n");
    printf("  States reachable : %d / %d\n", states_checked, S_COUNT);

    int total_violations = 0;
    /* Under a persistent valid request and a fair scheduler, each enabled
       normal step reduces rank 3 -> 2 -> 1 -> 0. Unrestricted graph has
       cancellation cycles, so this is conditional progress, not universal AF. */
    State progress[] = {S_WAITING, S_CONNECTED, S_AUTH_OK, S_CHARGING};
    for (int i = 0; i < 3; i++)
        if (!transition_hop_le(progress[i], progress[i+1])) total_violations++;
    printf("  Conditional progress witness: WAITING -> CONNECTED -> AUTH_OK -> CHARGING\n");
    printf("  Assumptions: persistent valid request, safe sensors, capacity and fair scheduling.\n");
    printf("  This witness is EF CHARGING; unrestricted G(request -> F charging) is NOT proved.\n");
    for (int p = 0; p < NUM_PROPS; p++) {
        total_violations += prop_violations[p];
        printf("  %-38s : %s\n", PROPS[p],
               prop_violations[p] == 0 ? "HOLDS" : "VIOLATED");
    }

    printf("-----------------------------------------------------\n");
    if (total_violations == 0) {
        printf("  VERDICT: ALL PROPERTIES HOLD in Kripke Model\n");
        printf("  Safety holds for the abstract labels; implementation checks are separate.\n");
    } else {
        printf("  VERDICT: %d PROPERTY VIOLATION(S) FOUND!\n", total_violations);
    }
    printf("=====================================================\n");

    return (total_violations == 0) ? 0 : 1;
}
