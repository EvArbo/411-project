CREATE TABLE IF NOT EXISTS workout_log (
    id INTEGER PRIMARY KEY,              
    name TEXT NOT NULL,                
    weight REAL NOT NULL,              
    repetitions INTEGER NOT NULL,      
    rpe REAL NOT NULL    
);


