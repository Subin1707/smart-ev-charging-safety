-- 004_create_indexes.sql
-- Danh chi muc toi uu hoa truy van

CREATE INDEX idx_telemetry_session_tick ON telemetry(session_id, tick);
CREATE INDEX idx_telemetry_vehicle ON telemetry(vehicle_code);
CREATE INDEX idx_safety_events_severity ON su_kien_an_toan(severity);
CREATE INDEX idx_safety_events_tick ON su_kien_an_toan(tick);
CREATE INDEX idx_phien_sac_active ON phien_sac(dang_hoat_dong);
