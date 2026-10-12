-- Smart EV Charging System SQL Persistence Dump
BEGIN TRANSACTION;

INSERT INTO phien_sac (id, vehicle_id, port_id, soc_bat_dau, dang_hoat_dong) VALUES (10, 1, 1, 20.00, TRUE) ON CONFLICT (id) DO NOTHING;
UPDATE phien_sac SET soc_ket_thuc = 50.00, nang_luong_kwh = 18.00, dang_hoat_dong = FALSE, ended_at = CURRENT_TIMESTAMP WHERE id = 10;

COMMIT;
