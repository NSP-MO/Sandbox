const express = require('express');
const pool = require('./database');
const app = express();

app.use(express.urlencoded({ extended: true }));
app.set('view engine', 'ejs');
app.use(express.static('public'));

// Helper functions
const generateID = (region) => `${region}-${Date.now()}`;

// Routes
app.get('/', async (req, res) => {
  try {
    const { rows } = await pool.query(`
      SELECT * FROM applicants 
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
  const id = generateID(region);
  
  try {
    await pool.query(
      'INSERT INTO applicants (id, name, address, region) VALUES ($1, $2, $3, $4)',
      [id, name, address, region]
    );
    res.redirect('/');
  } catch (err) {
    console.error(err);
    res.status(500).send('Submission failed');
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
        'UPDATE applicants SET status = 'verified' WHERE id = $1',
        [rows[0].id]
      );
    }
    res.redirect('/');
  } catch (err) {
    console.error(err);
    res.status(500).send('Processing failed');
  }
});

app.post('/edit/:id', async (req, res) => {
  const { name, address, region } = req.body;
  
  try {
    // Get current data
    const { rows } = await pool.query(
      'SELECT * FROM applicants WHERE id = $1',
      [req.params.id]
    );
    
    if (rows.length === 0) {
      return res.status(404).send('Applicant not found');
    }

    // Save to revisions
    await pool.query(
      `INSERT INTO revisions (applicant_id, name, address, region)
       VALUES ($1, $2, $3, $4)`,
      [req.params.id, rows[0].name, rows[0].address, rows[0].region]
    );

    // Update applicant
    await pool.query(
      `UPDATE applicants 
       SET name = $1, address = $2, region = $3, status = 'revision'
       WHERE id = $4`,
      [name, address, region, req.params.id]
    );
    
    res.redirect('/');
  } catch (err) {
    console.error(err);
    res.status(500).send('Update failed');
  }
});

app.post('/undo/:id', async (req, res) => {
  try {
    // Get last revision
    const { rows } = await pool.query(`
      SELECT * FROM revisions 
      WHERE applicant_id = $1 
      ORDER BY modified_at DESC 
      LIMIT 1
    `, [req.params.id]);

    if (rows.length > 0) {
      // Restore data
      await pool.query(
        `UPDATE applicants 
         SET name = $1, address = $2, region = $3 
         WHERE id = $4`,
        [rows[0].name, rows[0].address, rows[0].region, req.params.id]
      );

      // Delete revision
      await pool.query(
        'DELETE FROM revisions WHERE id = $1',
        [rows[0].id]
      );
    }
    
    res.redirect('/');
  } catch (err) {
    console.error(err);
    res.status(500).send('Undo failed');
  }
});

app.get('/sort/region', async (req, res) => {
  try {
    const { rows } = await pool.query(`
      SELECT * FROM applicants 
      WHERE status = 'pending'
      ORDER BY region
    `);
    res.render('index', { queue: rows });
  } catch (err) {
    console.error(err);
    res.status(500).send('Server Error');
  }
});

app.get('/sort/time', async (req, res) => {
  try {
    const { rows } = await pool.query(`
      SELECT * FROM applicants 
      WHERE status = 'pending'
      ORDER BY submission_time
    `);
    res.render('index', { queue: rows });
  } catch (err) {
    console.error(err);
    res.status(500).send('Server Error');
  }
});

app.listen(3000, () => console.log('Server running on port 3000'));