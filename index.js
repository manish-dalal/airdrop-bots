const express = require('express');
const bodyParser = require('body-parser');
const methods = require('./clicker');

const { clicker } = methods;

const app = express();
app.set('port', process.env.PORT || 4000);
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

app.get('/airdrop/clicker', (req, res) => {
  clicker();
  res.send('clicker started');
});

app.get('/', (req, res) => {
  res.send('Hello World!');
});

app.listen(app.get('port'), () => {
  console.log(`Example app listening on port ${app.get('port')}`);
});
