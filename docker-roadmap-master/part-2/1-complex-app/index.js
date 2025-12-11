const express = require('express');
const mongoose = require('mongoose');

const app = express();
const port = 3000;

// Set up mongoose connection
mongoose.connect("mongodb://localhost:27017", {});

const EntrySchema = new mongoose.Schema({
  text: String,
  date: { type: Date, default: Date.now },
});
// getting the db to talk to the backend application 
const Entry = mongoose.model('Entry', EntrySchema);

app.get('/', async (req, res) => {
  try {
    const entry = new Entry({ text: 'This is an entry by harkirat' });
    await entry.save();
    res.send('Entry added!');
  } catch (err) {
    res.status(500).send('Error occurred');
  }
});

app.listen(port, () => {
  console.log(`Example app listening on port ${port}`);
});



// how can backend talk to te