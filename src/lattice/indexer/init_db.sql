-- SQL script to create the ENTITY table
CREATE TABLE ENTITY (
    id TEXT PRIMARY KEY,
    function_name TEXT,
    namespace TEXT,
    definition TEXT,
    definition_embedding TEXT,
    function_name_embedding TEXT,
    description_embedding TEXT,

);

CREATE TABLE ENTITY_KEYWORD (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword TEXT
    embedding TEXT
    FOREIGN KEY (entity_id) REFERENCES ENTITY(id),
)


-- -- SQL script to create the RELATIONSHIP table
-- CREATE TABLE RELATIONSHIP (
--     id TEXT PRIMARY KEY,
--     source_id TEXT,
--     target_id TEXT,
--     line_number INTEGER,
--     arguments TEXT,
--     returns TEXT,
--     FOREIGN KEY (source_id) REFERENCES ENTITY(id),
--     FOREIGN KEY (target_id) REFERENCES ENTITY(id)
-- );