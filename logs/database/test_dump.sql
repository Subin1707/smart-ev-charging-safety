-- Smart EV Charging System SQL Persistence Dump
BEGIN TRANSACTION;

INSERT INTO xe_dien (id, ma_xe, dung_luong_kwh, soc_hien_tai, nhiet_do_c, cong_suat_sac_max_kw, trang_thai) VALUES (1, 'EV01', 60.00, 30.00, 30.00, 22.00, 'WAITING') ON CONFLICT (ma_xe) DO UPDATE SET soc_hien_tai = EXCLUDED.soc_hien_tai, nhiet_do_c = EXCLUDED.nhiet_do_c, trang_thai = EXCLUDED.trang_thai;

COMMIT;
