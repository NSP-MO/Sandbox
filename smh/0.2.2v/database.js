const { Pool } = require('pg');

const pool = new Pool({
  user: 'postgres',
  host: 'localhost',
  database: 'postgres',
  password: '797985',
  port: 5432,
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false
});

// Create tables
const initDB = async () => {
  try {
    await pool.query(`
      CREATE TABLE IF NOT EXISTS applicants (
        id VARCHAR(255) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        address TEXT NOT NULL,
        region VARCHAR(100) NOT NULL,
        submission_time TIMESTAMP DEFAULT NOW(),
        status VARCHAR(50) DEFAULT 'pending'
      );

      CREATE TABLE IF NOT EXISTS revisions (
        id SERIAL PRIMARY KEY,
        applicant_id VARCHAR(255) REFERENCES applicants(id),
        name VARCHAR(255),
        address TEXT,
        region VARCHAR(100),
        modified_at TIMESTAMP DEFAULT NOW()
      );
    `);
    console.log('Tables created successfully');
  } catch (err) {
    console.error('Error creating tables:', err);
  }
};

initDB();

module.exports = pool;