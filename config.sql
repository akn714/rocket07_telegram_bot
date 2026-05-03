-- Config table (only 1 row allowed)
CREATE TABLE IF NOT EXISTS config (
    id INTEGER PRIMARY KEY DEFAULT 1,
    delivery_charge INTEGER NOT NULL DEFAULT 9,
    is_delivery_closed TEXT NOT NULL DEFAULT 'false',
    single_row_guard BOOLEAN UNIQUE DEFAULT TRUE
);

-- Ensure only one row exists (optional insert)
INSERT INTO config (id, delivery_charge, is_delivery_closed)
VALUES (1, 9, 'false')
ON CONFLICT (id) DO NOTHING;

-- Enable Row Level Security
ALTER TABLE config ENABLE ROW LEVEL SECURITY;

-- Policies (adjust as needed)
CREATE POLICY "Enable read access for all" 
ON config FOR SELECT USING (true);

CREATE POLICY "Enable update access for all" 
ON config FOR UPDATE USING (true) WITH CHECK (true);

-- Update the variables using below sql
-- UPDATE config SET delivery_charge = 20, is_delivery_closed = true WHERE id = 1;