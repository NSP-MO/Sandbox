const mongoose = require('mongoose');

const applicantSchema = new mongoose.Schema({
  id: { type: String, unique: true },
  name: String,
  address: String,
  region: String,
  submissionTime: { type: Date, default: Date.now },
  status: { 
    type: String, 
    enum: ['pending', 'verified', 'revision'], 
    default: 'pending' 
  },
  revisions: [{
    name: String,
    address: String,
    region: String,
    modifiedAt: Date
  }]
});

module.exports = mongoose.model('Applicant', applicantSchema);