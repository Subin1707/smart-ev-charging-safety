-- 003_create_constraints.sql
-- Rang buoc CHECK an toan theo yeu cau

ALTER TABLE xe_dien
    ADD CONSTRAINT chk_xe_soc CHECK (soc_hien_tai >= 0.00 AND soc_hien_tai <= 100.00),
    ADD CONSTRAINT chk_xe_capacity CHECK (dung_luong_kwh > 0.00);

ALTER TABLE cong_sac
    ADD CONSTRAINT chk_port_number CHECK (port_number BETWEEN 1 AND 5),
    ADD CONSTRAINT chk_port_power CHECK (cong_suat_kw >= 0.00);

ALTER TABLE phien_sac
    ADD CONSTRAINT chk_session_soc_start CHECK (soc_bat_dau >= 0.00 AND soc_bat_dau <= 100.00),
    ADD CONSTRAINT chk_session_soc_end CHECK (soc_ket_thuc IS NULL OR (soc_ket_thuc >= 0.00 AND soc_ket_thuc <= 100.00)),
    ADD CONSTRAINT chk_session_energy CHECK (nang_luong_kwh >= 0.00);

ALTER TABLE telemetry
    ADD CONSTRAINT chk_telem_soc CHECK (soc >= 0.00 AND soc <= 100.00),
    ADD CONSTRAINT chk_telem_power CHECK (power_kw >= 0.00),
    ADD CONSTRAINT chk_telem_port CHECK (port_number BETWEEN 1 AND 5);
