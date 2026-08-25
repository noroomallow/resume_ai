PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    profile_photo TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS resumes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL DEFAULT 'Untitled Resume',
    full_name TEXT NOT NULL,
    professional_title TEXT,
    email TEXT NOT NULL,
    phone TEXT,
    location TEXT,
    website TEXT,
    linkedin TEXT,
    github TEXT,
    summary TEXT,
    template TEXT DEFAULT 'classic',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS education (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resume_id INTEGER NOT NULL,
    degree TEXT NOT NULL,
    institution TEXT NOT NULL,
    location TEXT,
    start_date TEXT,
    end_date TEXT,
    description TEXT,
    FOREIGN KEY (resume_id) REFERENCES resumes (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS experience (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resume_id INTEGER NOT NULL,
    company TEXT NOT NULL,
    position TEXT NOT NULL,
    location TEXT,
    start_date TEXT,
    end_date TEXT,
    description TEXT,
    FOREIGN KEY (resume_id) REFERENCES resumes (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resume_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    technologies TEXT,
    description TEXT,
    github_url TEXT,
    live_url TEXT,
    FOREIGN KEY (resume_id) REFERENCES resumes (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resume_id INTEGER NOT NULL,
    skill_name TEXT NOT NULL,
    category TEXT DEFAULT 'Technical',
    FOREIGN KEY (resume_id) REFERENCES resumes (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS certifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resume_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    issuer TEXT NOT NULL,
    date TEXT,
    credential_url TEXT,
    FOREIGN KEY (resume_id) REFERENCES resumes (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resume_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    date TEXT,
    FOREIGN KEY (resume_id) REFERENCES resumes (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS languages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resume_id INTEGER NOT NULL,
    language TEXT NOT NULL,
    proficiency TEXT,
    FOREIGN KEY (resume_id) REFERENCES resumes (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ats_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    resume_id INTEGER NOT NULL,
    job_title TEXT NOT NULL,
    job_description TEXT NOT NULL,
    score INTEGER NOT NULL,
    matched_keywords TEXT,
    missing_keywords TEXT,
    suggestions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (resume_id) REFERENCES resumes (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS portfolios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    resume_id INTEGER NOT NULL UNIQUE,
    username TEXT UNIQUE NOT NULL,
    theme TEXT DEFAULT 'modern',
    is_public INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (resume_id) REFERENCES resumes (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_resumes_user ON resumes(user_id);
CREATE INDEX IF NOT EXISTS idx_portfolios_username ON portfolios(username);