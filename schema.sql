CREATE TABLE Users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE,
    password TEXT
);

CREATE TABLE Dogs (
    id SERIAL PRIMARY KEY,
    dogname TEXT,
    owner_id INTEGER REFERENCES Users,
    UNIQUE (dogname, owner_id)
);

CREATE TABLE Skills (
    id SERIAL PRIMARY KEY,
    skill TEXT UNIQUE
);

CREATE TABLE Places (
    id SERIAL PRIMARY KEY,
    place TEXT UNIQUE
);

CREATE TABLE Disturbances (
    id SERIAL PRIMARY KEY,
    disturbance TEXT UNIQUE
);

CREATE TABLE Plan (
    id SERIAL PRIMARY KEY,
    dog_id INTEGER REFERENCES Dogs,
    skill_id INTEGER REFERENCES Skills,
    place_id INTEGER REFERENCES Places,
    disturbance_id INTEGER REFERENCES Disturbances,
    target_repeats INTEGER,
    visible BOOLEAN 
);

CREATE TABLE Progress (
    id SERIAL PRIMARY KEY,
    plan_id INTEGER REFERENCES Plan,
    repeated INTEGER
);