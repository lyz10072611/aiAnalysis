CREATE TABLE sites (
    site_id      SERIAL PRIMARY KEY,
    site_name    VARCHAR(100) NOT NULL UNIQUE,
    longitude    DOUBLE PRECISION NOT NULL,
    latitude     DOUBLE PRECISION NOT NULL
);
COMMENT ON TABLE sites IS '环境监测站点信息表';
COMMENT ON COLUMN sites.site_name IS '监测站点名称';
COMMENT ON COLUMN sites.longitude IS '地理经度';
COMMENT ON COLUMN sites.latitude IS '地理纬度';
CREATE TABLE pollutants (
    pollutant_id   SERIAL PRIMARY KEY,
    pollutant_name VARCHAR(50) NOT NULL UNIQUE
);

COMMENT ON TABLE pollutants IS '污染物类型表';
COMMENT ON COLUMN pollutants.pollutant_name IS '污染物名称';
CREATE TABLE measurements (
    distinct_id VARCHAR(50) PRIMARY KEY,
    site_id       INT NOT NULL,
    pollutant_id  INT NOT NULL,
    date          DATE NOT NULL,
    hour          INT NOT NULL CHECK (hour >= 0 AND hour <= 23),
    value         DOUBLE PRECISION,

    -- 外键约束
    FOREIGN KEY (site_id) REFERENCES sites(site_id),
    FOREIGN KEY (pollutant_id) REFERENCES pollutants(pollutant_id),

    -- 避免重复插入（同站点、同污染物、同日期+小时）
    CONSTRAINT unique_record UNIQUE (site_id, pollutant_id, date, hour)
);
COMMENT ON TABLE measurements IS '污染物实时监测数据表';
COMMENT ON COLUMN measurements.distinct_id IS '人工自然主键：date-hour site_id pollutant_id';
COMMENT ON COLUMN measurements.site_id IS '监测站点引用ID';
COMMENT ON COLUMN measurements.pollutant_id IS '污染物类型引用ID';
COMMENT ON COLUMN measurements.date IS '采样日期';
COMMENT ON COLUMN measurements.hour IS '采样小时(0-23)';
COMMENT ON COLUMN measurements.value IS '监测浓度数值';

COMMENT ON TABLE pollutants IS '污染物类型表';
COMMENT ON COLUMN pollutants.pollutant_name IS '污染物名称';
CREATE TABLE measurements_tif (
    distinct_id VARCHAR(50) PRIMARY KEY,
    site_id       INT NOT NULL,
    pollutant_id  INT NOT NULL,
    date          DATE NOT NULL,
    hour          INT NOT NULL CHECK (hour >= 0 AND hour <= 23),
    value         DOUBLE PRECISION,
    data_dir      VARCHAR(80) NOT NULL,

    -- 外键约束
    FOREIGN KEY (site_id) REFERENCES sites(site_id),
    FOREIGN KEY (pollutant_id) REFERENCES pollutants(pollutant_id),

    -- 避免重复插入（同站点、同污染物、同日期+小时）
    CONSTRAINT unique_record2 UNIQUE (site_id, pollutant_id, date, hour)
);
COMMENT ON TABLE measurements_tif IS 'tif中提取监测数据表';
COMMENT ON COLUMN measurements_tif.site_id IS '监测站点引用ID';
COMMENT ON COLUMN measurements_tif.pollutant_id IS '污染物类型引用ID';
COMMENT ON COLUMN measurements_tif.date IS '采样日期';
COMMENT ON COLUMN measurements_tif.hour IS '采样小时(0-23)';
COMMENT ON COLUMN measurements_tif.value IS '监测浓度数值';
COMMENT ON COLUMN measurements_tif.data_dir IS 'tif数据存放路径';
-- 插入监测点数据到sites表
INSERT INTO sites (site_name, longitude, latitude) VALUES
('东城东四', 116.417, 39.929),
('东城天坛', 116.407, 39.886),
('西城官园', 116.339, 39.929),
('西城万寿西宫', 116.352, 39.878),
('朝阳奥体中心', 116.397, 39.982),
('朝阳农展馆', 116.461, 39.937),
('海淀万柳', 116.287, 39.987),
('海淀四季青', 116.23052, 40.03),
('丰台小屯', 116.25528, 39.87694),
('丰台云岗', 116.146, 39.824),
('石景山古城', 116.176, 39.914),
('石景山老山', 116.20764, 39.90886),
('昌平镇', 116.234, 40.217),
('昌平南邵', 116.27603, 40.21651),
('定陵(对照点)', 116.22, 40.292),
('延庆夏都', 115.972, 40.453),
('延庆石河营', 116.00138, 40.46327),
('怀柔镇', 116.628, 40.328),
('怀柔新城', 116.6018, 40.3118),
('密云镇', 116.832, 40.37),
('密云新城', 116.85152, 40.4088),
('平谷镇', 117.118, 40.143),
('平谷新城', 117.0854, 40.15353),
('顺义新城', 116.655, 40.127),
('顺义北小营', 116.6853, 40.16087),
('通州永顺', 116.67503, 39.93435),
('通州东关', 116.6996, 39.9131),
('大兴黄村', 116.404, 39.718),
('大兴旧宫', 116.47456, 39.78284),
('亦庄开发区', 116.506, 39.795),
('京东南区域点', 116.78437, 39.63606),
('门头沟双峪', 116.106, 39.937),
('门头沟三家店', 116.09122, 39.96926),
('房山良乡', 116.136, 39.742),
('房山燕山', 115.96916, 39.76419)
ON CONFLICT (site_name) DO NOTHING;

INSERT INTO pollutants (pollutant_id,pollutant_name) VALUES(1,'NO2')


-- 对于站点数据 的插入执行。/tools/importMeasurements.py
-- 对于tif数据 的插入执行。/tools/importTifMeasurements.py