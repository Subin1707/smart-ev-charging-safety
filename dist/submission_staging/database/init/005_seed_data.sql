-- 005_seed_data.sql
-- Khoi tao du lieu goc cho tram sac va 5 cong sac

INSERT INTO tram_sac (id, ma_tram, so_cong, cong_suat_toi_da_kw, trang_thai)
VALUES (1, 'STATION-01', 5, 100.00, 'OPERATIONAL')
ON CONFLICT (ma_tram) DO NOTHING;

INSERT INTO cong_sac (tram_id, port_number, trang_thai, dien_ap_v, dong_dien_a, cong_suat_kw)
VALUES 
    (1, 1, 'IDLE', 400.00, 0.00, 0.00),
    (1, 2, 'IDLE', 400.00, 0.00, 0.00),
    (1, 3, 'IDLE', 400.00, 0.00, 0.00),
    (1, 4, 'IDLE', 400.00, 0.00, 0.00),
    (1, 5, 'IDLE', 400.00, 0.00, 0.00)
ON CONFLICT (tram_id, port_number) DO NOTHING;
