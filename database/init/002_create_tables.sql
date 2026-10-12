-- 002_create_tables.sql
-- Tao 6 bang co so du lieu cot loi

DROP TABLE IF EXISTS telemetry CASCADE;
DROP TABLE IF EXISTS su_kien_an_toan CASCADE;
DROP TABLE IF EXISTS phien_sac CASCADE;
DROP TABLE IF EXISTS cong_sac CASCADE;
DROP TABLE IF EXISTS tram_sac CASCADE;
DROP TABLE IF EXISTS xe_dien CASCADE;

CREATE TABLE tram_sac (
    id SERIAL PRIMARY KEY,
    ma_tram VARCHAR(20) NOT NULL UNIQUE,
    so_cong INT NOT NULL DEFAULT 5,
    cong_suat_toi_da_kw NUMERIC(6, 2) NOT NULL DEFAULT 100.00,
    trang_thai VARCHAR(20) NOT NULL DEFAULT 'OPERATIONAL',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE cong_sac (
    id SERIAL PRIMARY KEY,
    tram_id INT NOT NULL REFERENCES tram_sac(id) ON DELETE CASCADE,
    port_number INT NOT NULL,
    trang_thai VARCHAR(20) NOT NULL DEFAULT 'IDLE',
    dien_ap_v NUMERIC(6, 2) DEFAULT 400.00,
    dong_dien_a NUMERIC(6, 2) DEFAULT 0.00,
    cong_suat_kw NUMERIC(6, 2) DEFAULT 0.00,
    ma_loi INT DEFAULT 0,
    CONSTRAINT uq_tram_port UNIQUE (tram_id, port_number)
);

CREATE TABLE xe_dien (
    id SERIAL PRIMARY KEY,
    ma_xe VARCHAR(20) NOT NULL UNIQUE,
    dung_luong_kwh NUMERIC(6, 2) NOT NULL,
    soc_hien_tai NUMERIC(5, 2) NOT NULL,
    nhiet_do_c NUMERIC(5, 2) NOT NULL,
    cong_suat_sac_max_kw NUMERIC(5, 2) NOT NULL DEFAULT 22.00,
    trang_thai VARCHAR(20) NOT NULL DEFAULT 'WAITING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE phien_sac (
    id SERIAL PRIMARY KEY,
    vehicle_id INT NOT NULL REFERENCES xe_dien(id) ON DELETE CASCADE,
    port_id INT NOT NULL REFERENCES cong_sac(id) ON DELETE CASCADE,
    soc_bat_dau NUMERIC(5, 2) NOT NULL,
    soc_ket_thuc NUMERIC(5, 2),
    nang_luong_kwh NUMERIC(6, 2) DEFAULT 0.00,
    dang_hoat_dong BOOLEAN DEFAULT TRUE,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP
);

CREATE TABLE telemetry (
    id SERIAL PRIMARY KEY,
    session_id INT REFERENCES phien_sac(id) ON DELETE CASCADE,
    tick INT NOT NULL,
    vehicle_code VARCHAR(20) NOT NULL,
    port_number INT NOT NULL,
    soc NUMERIC(5, 2) NOT NULL,
    temperature_c NUMERIC(5, 2) NOT NULL,
    power_kw NUMERIC(6, 2) NOT NULL,
    state VARCHAR(20) NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE su_kien_an_toan (
    id SERIAL PRIMARY KEY,
    tick INT NOT NULL,
    vehicle_code VARCHAR(20) NOT NULL,
    port_number INT NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
