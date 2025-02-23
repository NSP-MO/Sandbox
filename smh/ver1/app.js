const express = require('express');
const mongoose = require('mongoose');
const bodyParser = require('body-parser');
const Applicant = require('./models/Applicant');

const app = express();

// Database connection
mongoose.connect('mongodb://localhost:27017/ktp-system', {
  useNewUrlParser: true,
  useUnifiedTopology: true
});

// Middleware
app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.static('public'));
app.set('view engine', 'ejs');

// Routes
app.get('/', async (req, res) => {
  const queue = await Applicant.find({ status: 'pending' }).sort({ submissionTime: 1 });
  res.render('index', { queue });
});

app.post('/submit', async (req, res) => {
  const newApplicant = new Applicant({
    id: generateID(req.body.region),
    ...req.body,
    status: 'pending'
  });
  await newApplicant.save();
  res.redirect('/');
});

app.post('/process', async (req, res) => {
  const nextApplicant = await Applicant.findOne({ status: 'pending' }).sort({ submissionTime: 1 });
  if (nextApplicant) {
    nextApplicant.status = 'verified';
    await nextApplicant.save();
  }
  res.redirect('/');
});

app.post('/edit/:id', async (req, res) => {
  const applicant = await Applicant.findById(req.params.id);
  applicant.revisions.push({
    name: applicant.name,
    address: applicant.address,
    region: applicant.region,
    modifiedAt: Date.now()
  });
  Object.assign(applicant, req.body);
  applicant.status = 'revision';
  await applicant.save();
  res.redirect('/');
});

app.post('/undo/:id', async (req, res) => {
  const applicant = await Applicant.findById(req.params.id);
  if (applicant.revisions.length > 0) {
    const lastRevision = applicant.revisions.pop();
    Object.assign(applicant, lastRevision);
    await applicant.save();
  }
  res.redirect('/');
});

app.get('/sort/region', async (req, res) => {
  const queue = await Applicant.find({ status: 'pending' }).sort({ region: 1 });
  res.render('index', { queue });
});

app.get('/sort/time', async (req, res) => {
  const queue = await Applicant.find({ status: 'pending' }).sort({ submissionTime: 1 });
  res.render('index', { queue });
});

function generateID(region) {
  return `${region}-${Date.now()}`;
}

app.listen(3000, () => console.log('Server running on http://localhost:3000'));