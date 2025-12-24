CREATE EXTENSION IF NOT EXISTS vector;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user' CHECK (role IN ('user', 'admin')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

CREATE TABLE IF NOT EXISTS cvs (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) UNIQUE NOT NULL,
    
    name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    location JSONB,  
    
    summary TEXT,
    work_experience JSONB,  
    education JSONB,        
    skills JSONB,           
    certifications JSONB,   
    languages JSONB,        
    
    raw_text TEXT,          
    parsed_data JSONB,     
    
    embedding vector(384),  
    
    total_experience INTEGER DEFAULT 0, 
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_cvs_email ON cvs(email);
CREATE INDEX IF NOT EXISTS idx_cvs_name ON cvs(name);
CREATE INDEX IF NOT EXISTS idx_cvs_created_at ON cvs(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_cvs_embedding ON cvs 
USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_cvs_skills ON cvs USING GIN (skills);
CREATE INDEX IF NOT EXISTS idx_cvs_work_experience ON cvs USING GIN (work_experience);


CREATE TABLE IF NOT EXISTS jobs (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(100) UNIQUE NOT NULL,
    
    title VARCHAR(255) NOT NULL,
    company VARCHAR(255),
    description TEXT,
    location VARCHAR(255),
    
    requirements JSONB,
    skills_required JSONB,  
    
    experience_years JSONB,
    
    education_required JSONB,
    
    embedding vector(384),
    
    salary_range JSONB, 
    remote_allowed BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_jobs_job_id ON jobs(job_id);
CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company);
CREATE INDEX IF NOT EXISTS idx_jobs_title ON jobs(title);
CREATE INDEX IF NOT EXISTS idx_jobs_is_active ON jobs(is_active);
CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON jobs(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_jobs_embedding ON jobs 
USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_jobs_skills_required ON jobs USING GIN (skills_required);
CREATE INDEX IF NOT EXISTS idx_jobs_requirements ON jobs USING GIN (requirements);


CREATE TABLE IF NOT EXISTS recommendations (
    id SERIAL PRIMARY KEY,
    cv_id INTEGER REFERENCES cvs(id) ON DELETE CASCADE,
    job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
    
    match_score FLOAT NOT NULL,
    skills_match FLOAT,
    experience_match FLOAT,
    education_match FLOAT,
    semantic_similarity FLOAT,
    
    matched_skills JSONB,   
    missing_skills JSONB,   
    explanation TEXT,       
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL '24 hours'),
    
    UNIQUE(cv_id, job_id)
);

CREATE INDEX IF NOT EXISTS idx_recommendations_cv_id ON recommendations(cv_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_job_id ON recommendations(job_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_match_score ON recommendations(match_score DESC);
CREATE INDEX IF NOT EXISTS idx_recommendations_created_at ON recommendations(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_recommendations_expires_at ON recommendations(expires_at);

CREATE INDEX IF NOT EXISTS idx_recommendations_cv_score ON recommendations(cv_id, match_score DESC);

CREATE TABLE IF NOT EXISTS user_cvs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    cv_id INTEGER REFERENCES cvs(id) ON DELETE CASCADE,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id, cv_id)
);

CREATE INDEX IF NOT EXISTS idx_user_cvs_user_id ON user_cvs(user_id);
CREATE INDEX IF NOT EXISTS idx_user_cvs_cv_id ON user_cvs(cv_id);
CREATE INDEX IF NOT EXISTS idx_user_cvs_uploaded_at ON user_cvs(uploaded_at DESC);

-- Function to update updated_at timestamp automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to tables with updated_at column
DROP TRIGGER IF EXISTS update_cvs_updated_at ON cvs;
CREATE TRIGGER update_cvs_updated_at 
    BEFORE UPDATE ON cvs
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_jobs_updated_at ON jobs;
CREATE TRIGGER update_jobs_updated_at 
    BEFORE UPDATE ON jobs
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

