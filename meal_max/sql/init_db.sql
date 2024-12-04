DROP TABLE IF EXISTS workout_log;
CREATE TABLE workout_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,              
    name TEXT NOT NULL,                
    weight REAL NOT NULL,              
    sets INTEGER NOT NULL,
    repetitions INTEGER NOT NULL,      
    rpe REAL NOT NULL,
    deleted BOOLEAN DEFAULT FALSE
   
);


