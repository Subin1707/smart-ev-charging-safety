# SMART EV FORMAL COVERAGE

- Requirements: 11/11 mapped
- Constraints: 19/19 mapped
- Formal properties: 15
- Violation predicates: 11
- States generated: 19
- Reachable states: 19
- Unreachable states: 0
- Transitions generated: 25
- Reachable transitions: 25
- Boundary scenarios: 14
- Negative scenarios: 3
- Sequence scenarios: 7
- Unmapped requirements: 0
- Unmapped constraints: 0
- Orphan violation labels: 0
- Invalid transitions: 0
- READY_FOR_TEACHER_APP: YES

## Requirement Coverage

| Requirement | Constraints | Violation Predicate | Formal Property | States | Transitions | Scenarios |
|---|---|---|---|---:|---:|---|
| `REQ-AUTH-01` | `AUTH-01`<br>`AUTH-02` | `req_auth_01_violation` | `AG(!req_auth_01_violation)` | 4 | 4 | `auth_failure_start_blocked`<br>`normal_connect_auth_start` |
| `REQ-AUTH-02` | `AUTH-03`<br>`AUTH-04` | `req_auth_02_violation` | `AG(!req_auth_02_violation)` | 1 | 2 | `disconnect_after_stop`<br>`disconnect_clears_auth` |
| `REQ-SOC-01` | `BAT-01` | `req_soc_01_violation` | `AG(!req_soc_01_violation)` | 3 | 4 | `soc_boundary`<br>`soc_boundary_invalid` |
| `REQ-SOC-02` | `BAT-02` | `req_soc_02_violation` | `AG(!req_soc_02_violation)` | 2 | 3 | `charging_soc_full_stop`<br>`disconnect_after_stop`<br>`soc_boundary` |
| `REQ-TEMP-01` | `BAT-03` | `req_temp_01_violation` | `AG(!req_temp_01_violation)` | 5 | 7 | `charging_overheat_stop`<br>`overheat_recovery`<br>`temperature_boundary`<br>`temperature_boundary_invalid` |
| `REQ-PORT-01` | `PORT-01` | `req_port_01_violation` | `AG(!req_port_01_violation)` | 1 | 1 | `normal_connect_auth_start` |
| `REQ-PORT-02` | `PORT-04`<br>`PORT-05` | `req_port_02_violation` | `AG(!req_port_02_violation)` | 1 | 1 | `port_exclusivity_negative` |
| `REQ-PORT-03` | `PORT-03` | `req_port_03_violation` | `AG(!req_port_03_violation)` | 1 | 2 | `charging_port_fault_stop`<br>`fault_recovery` |
| `REQ-CHG-01` | `CHG-01`<br>`CHG-02`<br>`CHG-03`<br>`CHG-04`<br>`CHG-05`<br>`CHG-08` | `req_chg_01_violation` | `AG(!req_chg_01_violation)` | 3 | 4 | `auth_failure_start_blocked`<br>`normal_connect_auth_start`<br>`soc_boundary`<br>`temperature_boundary` |
| `REQ-CHG-02` | `CHG-08` | `req_chg_02_violation` | `AG(!req_chg_02_violation)` | 2 | 3 | `normal_connect_auth_start`<br>`overheat_recovery`<br>`recovery_restart` |
| `REQ-EMG-01` | `CHG-06`<br>`CHG-07` | `req_emg_01_violation` | `AG(!req_emg_01_violation)` | 3 | 4 | `charging_emergency_stop`<br>`charging_port_fault_stop`<br>`emergency_recovery`<br>`fault_recovery` |
