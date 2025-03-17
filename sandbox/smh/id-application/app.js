const express = require('express');
const { Pool } = require('pg');
const app = express();

// PostgreSQL connection
const pool = new Pool({
  user: 'postgres',
  host: 'localhost',
  database: 'id-application',
  password: '797985',
  port: 5432,
});

app.use(express.urlencoded({ extended: true }));
app.set('view engine', 'ejs');
app.use(express.static('public'));

// Routes
app.get('/', async (req, res) => {
  try {
    const { rows } = await pool.query(`
      SELECT *, TO_CHAR(submission_time, 'YYYY-MM-DD HH24:MI:SS') as formatted_time 
      FROM applicants 
      WHERE status = 'pending'
      ORDER BY submission_time
    `);
    res.render('index', { queue: rows });
  } catch (err) {
    console.error(err);
    res.status(500).send('Server Error');
  }
});

app.post('/submit', async (req, res) => {
  const { name, address, region } = req.body;
  const id = `${region}-${Date.now()}`;

  try {
    await pool.query(
      'INSERT INTO applicants (id, name, address, region) VALUES ($1, $2, $3, $4)',
      [id, name, address, region]
    );
    res.redirect('/');
  } catch (err) {
    console.error(err);
    res.status(500).send('Submission Error');
  }
});

app.post('/process', async (req, res) => {
  try {
    const { rows } = await pool.query(`
      SELECT * FROM applicants 
      WHERE status = 'pending'
      ORDER BY submission_time
      LIMIT 1
    `);
    
    if (rows.length > 0) {
      await pool.query(
        'UPDATE applicants SET status = $1 WHERE id = $2',
        ['verified', rows[0].id]
      );
    }
    res.redirect('/');
  } catch (err) {
    console.error(err);
    res.status(500).send('Processing Error');
  }
});

// Add other routes (edit, undo, sort) from previous implementation

app.listen(3000, () => console.log('Server running on http://localhost:3000'));