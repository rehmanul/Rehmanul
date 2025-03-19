-- Database schema for Web Stryker R7

CREATE TABLE IF NOT EXISTS extractions (
    id VARCHAR(64) PRIMARY KEY,
    url TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    title TEXT,
    content JSON,
    metadata JSON,
    error_message TEXT,
    category VARCHAR(50),
    source_type VARCHAR(30),
    extraction_time FLOAT,
    retry_count INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_extractions_status ON extractions(status);
CREATE INDEX IF NOT EXISTS idx_extractions_created_at ON extractions(created_at);
CREATE INDEX IF NOT EXISTS idx_extractions_category ON extractions(category);

CREATE TABLE IF NOT EXISTS extraction_logs (
    id SERIAL PRIMARY KEY,
    extraction_id VARCHAR(64) REFERENCES extractions(id),
    event_type VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    level VARCHAR(20) DEFAULT 'INFO',
    details JSON
);

CREATE INDEX IF NOT EXISTS idx_extraction_logs_extraction_id ON extraction_logs(extraction_id);
CREATE INDEX IF NOT EXISTS idx_extraction_logs_level ON extraction_logs(level);

CREATE TABLE IF NOT EXISTS extraction_results (
    id SERIAL PRIMARY KEY,
    extraction_id VARCHAR(64) REFERENCES extractions(id),
    content_type VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSON
);

CREATE INDEX IF NOT EXISTS idx_extraction_results_extraction_id ON extraction_results(extraction_id);

-- Functions for updating timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for automatic timestamp updates
CREATE TRIGGER update_extraction_updated_at
    BEFORE UPDATE ON extractions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
