# Requirement Audit - Phase 1

Scope: audit the 11 normalized Smart EV requirements before generating the V2 formal model.

Pass criteria:

- Requirements audited: 11/11
- Missing semantics: 0
- Missing production mapping: 0

## Domain Coverage

| Domain | Requirements | Audit Result |
|---|---:|---|
| AUTH | 2 | COMPLETE |
| BATTERY / SOC | 2 | COMPLETE |
| TEMPERATURE | 1 | COMPLETE |
| PORT | 3 | COMPLETE |
| CHARGING | 2 | COMPLETE |
| EMERGENCY | 1 | COMPLETE |

## REQ-AUTH-01

```yaml
Domain: AUTH
Requirement: Vehicle authentication may succeed only when the vehicle is connected and the token is valid.
Constraints:
  - AUTH-01: A -> C
  - AUTH-02: A -> T

Input:
  - connected
  - token_valid
  - authentication request/result

Normal:
  - authenticated implies connected
  - authenticated implies token_valid

Unsafe:
  - authenticated while disconnected
  - authenticated with an invalid token

Violation:
  - authenticated && (!connected || !token_valid)

Violation label:
  - req_auth_01_violation

Relevant events:
  - connect
  - valid_token
  - authenticate_success
  - start_charging

Production:
  - xac_thuc_xe()
  - ket_noi_xe_vao_tram()
  - kiem_tra_sr02_xac_thuc()

Status: COMPLETE
```

## REQ-AUTH-02

```yaml
Domain: AUTH
Requirement: When a vehicle disconnects from the station, authentication must be cleared.
Constraints:
  - AUTH-03: !C -> !A
  - AUTH-04: X -> next(!A)

Input:
  - connected
  - authenticated
  - disconnect_request

Normal:
  - disconnected vehicle is not authenticated
  - disconnect completion clears authentication state

Unsafe:
  - disconnected vehicle remains authenticated

Violation:
  - disconnected && authenticated

Violation label:
  - req_auth_02_violation

Relevant events:
  - disconnect_request
  - disconnect_complete
  - vehicle_disconnect

Production:
  - ngat_ket_noi_xe_khoi_tram()
  - ngat_ket_noi_cong()

Status: COMPLETE
```

## REQ-SOC-01

```yaml
Domain: BATTERY / SOC
Requirement: Vehicle SOC must remain between 0% and 100%.
Constraints:
  - BAT-01: 0 <= soc <= 100

Input:
  - soc
  - battery update
  - SOC sensor/classification result

Normal:
  - 0 <= soc <= 100
  - SOC class is SOC_OK or SOC_FULL

Unsafe:
  - soc < 0
  - soc > 100
  - SOC class is SOC_INVALID

Violation:
  - soc_out_of_range

Violation label:
  - req_soc_01_violation

Relevant events:
  - soc_update
  - battery_tick
  - sensor_read
  - monitor_tick

Production:
  - soc_hop_le()
  - cap_nhat_pin()
  - kiem_tra_sr06_soc_hop_le()

Status: COMPLETE
```

## REQ-SOC-02

```yaml
Domain: BATTERY / SOC
Requirement: A vehicle with SOC at 100% must not continue receiving charging power.
Constraints:
  - BAT-02: SOC_FULL -> !CHARGING

Input:
  - soc
  - charging
  - power_positive

Normal:
  - SOC_FULL implies charging is stopped
  - SOC_FULL implies charging power is zero

Unsafe:
  - SOC_FULL while charging continues
  - SOC_FULL while power remains positive

Violation:
  - soc_full && (charging || power_positive)

Violation label:
  - req_soc_02_violation

Relevant events:
  - start_charging
  - soc_full
  - monitor_tick
  - power_update

Production:
  - co_the_bat_dau_sac()
  - giam_sat_xe_va_cong()
  - kiem_tra_sr04_pin_day()

Status: COMPLETE
```

## REQ-TEMP-01

```yaml
Domain: TEMPERATURE
Requirement: When battery temperature reaches or exceeds 60 C, charging must stop.
Constraints:
  - BAT-03: TEMP_OVERHEAT -> !CHARGING

Input:
  - temperature
  - charging
  - power_positive

Normal:
  - temperature < 60 C while charging is allowed
  - temperature >= 60 C forces stopped charging and zero power

Unsafe:
  - temperature >= 60 C while charging continues
  - temperature >= 60 C while power remains positive

Violation:
  - overheat && charging

Violation label:
  - req_temp_01_violation

Relevant events:
  - temperature_rise
  - start_charging
  - monitor_tick
  - safety_cutoff

Production:
  - pin_qua_nhiet()
  - co_the_bat_dau_sac()
  - giam_sat_xe_va_cong()
  - kiem_tra_sr03_nhiet_do()

Status: COMPLETE
```

## REQ-PORT-01

```yaml
Domain: PORT
Requirement: A port may enter CHARGING only when a valid vehicle is connected.
Constraints:
  - PORT-01: P -> C

Input:
  - port connected flag
  - vehicle assignment
  - charging request/state

Normal:
  - charging port has a connected vehicle
  - port vehicle_id matches the assigned vehicle

Unsafe:
  - port is charging without a connected vehicle

Violation:
  - charging && !connected

Violation label:
  - req_port_01_violation

Relevant events:
  - vehicle_connect
  - start_charging
  - vehicle_disconnect
  - connection_lost

Production:
  - ket_noi_xe_vao_cong()
  - ket_noi_xe_vao_tram()
  - co_the_bat_dau_sac()

Status: COMPLETE
```

## REQ-PORT-02

```yaml
Domain: PORT
Requirement: At any time, one charging port may be linked to at most one vehicle.
Constraints:
  - PORT-04: vehicles_per_port <= 1
  - PORT-05: ports_per_vehicle <= 1

Input:
  - port occupancy
  - vehicle_id
  - assigned_port
  - connect request

Normal:
  - one port has at most one vehicle
  - one vehicle occupies at most one port

Unsafe:
  - second vehicle is linked to an occupied port
  - same vehicle is linked to multiple ports

Violation:
  - port_multi_vehicle

Violation label:
  - req_port_02_violation

Relevant events:
  - vehicle_connect
  - second_vehicle_attempt
  - repeated_connect
  - auto_port_assignment

Production:
  - ket_noi_xe_vao_cong()
  - ket_noi_xe_vao_tram()
  - kiem_tra_sr07_doc_quyen_cong()

Status: COMPLETE
```

## REQ-PORT-03

```yaml
Domain: PORT
Requirement: A faulted port must not deliver charging power.
Constraints:
  - PORT-03: F -> !P

Input:
  - fault
  - charging
  - power_positive

Normal:
  - faulted port is not charging
  - faulted port has zero power/current

Unsafe:
  - faulted port remains charging
  - faulted port delivers positive power

Violation:
  - fault && (charging || power_positive)

Violation label:
  - req_port_03_violation

Relevant events:
  - fault_detected
  - emergency_stop
  - monitor_tick
  - power_update

Production:
  - kich_hoat_dung_khan_cap_cong()
  - giam_sat_xe_va_cong()
  - kiem_tra_sr08_ma_loi()

Status: COMPLETE
```

## REQ-CHG-01

```yaml
Domain: CHARGING
Requirement: Charging may start only when the vehicle is connected, authenticated, battery and temperature are safe, the port is ready, and no emergency or fault is active.
Constraints:
  - CHG-01: CHARGING -> C
  - CHG-02: CHARGING -> A
  - CHG-03: CHARGING -> B
  - CHG-04: CHARGING -> T
  - CHG-05: CHARGING -> P
  - CHG-08: CHARGING -> VALID

Input:
  - connected
  - authenticated
  - battery_safe
  - temperature_safe
  - port_ready
  - emergency
  - fault
  - start_charging request

Normal:
  - charging starts only when the complete safety gate is valid
  - VALID = connected && authenticated && battery_safe && temperature_safe && port_ready && !emergency && !fault

Unsafe:
  - charging starts while any safety-gate input is false

Violation:
  - charging && !safety_gate_valid

Violation label:
  - req_chg_01_violation

Relevant events:
  - start_charging
  - authenticate_failure
  - battery_unsafe
  - temperature_unsafe
  - port_not_ready
  - emergency_triggered
  - fault_detected

Production:
  - co_the_bat_dau_sac()
  - bat_dau_sac()
  - giam_sat_xe_va_cong()

Status: COMPLETE
```

## REQ-CHG-02

```yaml
Domain: CHARGING
Requirement: Charging requires the complete safety gate to remain valid.
Constraints:
  - CHG-08: CHARGING -> VALID

Input:
  - active charging session
  - connected
  - authenticated
  - battery_safe
  - temperature_safe
  - port_ready
  - emergency
  - fault

Normal:
  - while charging, the full safety gate remains true
  - if the safety gate becomes false, charging is stopped or blocked

Unsafe:
  - charging continues after any safety condition is lost

Violation:
  - charging && !safety_gate_valid

Violation label:
  - req_chg_02_violation

Relevant events:
  - monitor_tick
  - connection_lost
  - authentication_lost
  - battery_unsafe
  - temperature_unsafe
  - port_not_ready
  - emergency_triggered
  - fault_detected

Production:
  - co_the_bat_dau_sac()
  - kiem_tra_toan_bo_tram()

Status: COMPLETE
```

## REQ-EMG-01

```yaml
Domain: EMERGENCY
Requirement: Emergency or fault conditions must stop charging and force charging power to zero.
Constraints:
  - CHG-06: E -> !CHARGING
  - CHG-07: F -> !CHARGING

Input:
  - emergency
  - fault
  - charging
  - power_positive

Normal:
  - emergency implies not charging
  - fault implies not charging
  - emergency or fault forces power to zero

Unsafe:
  - emergency while charging continues
  - fault while charging continues
  - emergency or fault while power remains positive

Violation:
  - (emergency || fault) && (charging || power_positive)

Violation label:
  - req_emg_01_violation

Relevant events:
  - emergency_triggered
  - emergency_stop
  - fault_detected
  - monitor_tick

Production:
  - kich_hoat_dung_khan_cap_cong()
  - kich_hoat_dung_khan_cap_tram()
  - kiem_tra_sr05_khan_cap()

Status: COMPLETE
```

## Phase 1 Gate

```yaml
Requirements audited: 11/11
Missing semantics: 0
Missing production mapping: 0
Status: PASS
```
