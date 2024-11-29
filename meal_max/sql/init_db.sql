CREATE TABLE IF NOT EXISTS workout_logs (
    id TEXT PRIMARY KEY,
    date DATETIME,
    exercise TEXT,
    duration INTEGER,
    intensity TEXT,
    notes TEXT
);


