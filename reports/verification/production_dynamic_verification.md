# GD9.5 Production Dynamic/Fuzz Verification

Generated: 2026-09-29T08:51:47.190049+00:00

- Normal dynamic status: PASS
- Boundary cases executed: 14
- Boolean combinations executed: 128
- Runtime failures: 0
- ASan: UNAVAILABLE
- UBSan: UNAVAILABLE
- Production harness: 11/11
- Negative control: DETECTED

## Requirement Targets

| Requirement | Dynamic target groups |
|---|---|
| REQ-AUTH-01 | authentication_valid_invalid_tokens |
| REQ-AUTH-02 | disconnect_clears_authentication |
| REQ-SOC-01 | soc_boundaries |
| REQ-SOC-02 | soc_full_blocks_and_monitor_stops |
| REQ-TEMP-01 | temperature_boundaries |
| REQ-PORT-01 | port_connection_required |
| REQ-PORT-02 | port_exclusivity |
| REQ-PORT-03 | fault_port_power_zero |
| REQ-CHG-01 | charging_gate_boolean_enumeration |
| REQ-CHG-02 | station_monitor_all_ports |
| REQ-EMG-01 | emergency_zero_power |
