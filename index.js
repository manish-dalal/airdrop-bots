const express = require('express');
const bodyParser = require('body-parser');
const methods = require('./clicker');
const axios = require('axios');

const { getActiveUserBot } = methods;

const app = express();
app.set('port', process.env.PORT || 4000);
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

const sleep = (ms) => {
  return new Promise((resolve) => setTimeout(resolve, ms));
};

app.get('/', (req, res) => {
  res.send('Hello World!');
});

const fetchWithNoError = (url) =>
  new Promise(async (resolve) => {
    try {
      await axios.get(url);
      resolve({});
    } catch (error) {
      resolve({});
    } finally {
      resolve({});
    }
  });

const startHamsterWakeScript = async () => {
  await fetchWithNoError('https://hamster-1.glitch.me/wake-other');
  await sleep(60000);
  await fetchWithNoError('https://hamster-1.glitch.me/wake-other');
  await sleep(60000);
  await fetchWithNoError('https://hamster-1.glitch.me/wake-other');
  await sleep(20000);
  await fetchWithNoError('https://hamster-1.glitch.me/claim-other');
  await sleep(60000);
  await fetchWithNoError('https://hamster-1.glitch.me/wake-other');
  await sleep(60000);
  await fetchWithNoError('https://hamster-1.glitch.me/wake-other');
  await sleep(60000);
  await fetchWithNoError('https://hamster-1.glitch.me/wake-other');
};

const randomIntFromInterval = (min, max) => {
  // min and max included
  return Math.floor(Math.random() * (max - min + 1) + min);
};
let oldInterval = null;
let randomTimeout = randomIntFromInterval(3, 28);

app.get('/start-hamster-bots', (req, res) => {
  const maxStartTime = parseInt(req.query && req.query.maxTime) || 28;
  oldInterval && clearTimeout(oldInterval);
  randomTimeout = randomIntFromInterval(3, maxStartTime);
  console.log('Starts in ', randomTimeout, ' mins');

  oldInterval = setTimeout(startHamsterWakeScript, 60000 * randomTimeout);
  res.send('Started hamster bots');
});

app.get('/start-hamster-instant', (req, res) => {
  startHamsterWakeScript()
  res.send('Started hamster bots instant');
});

app.get('/get-next-start', (req, res) => {
  res.send(`${randomTimeout}`);
});


app.get('/get-stats', (req, res) => {
  const stats = getActiveUserBot()
  res.send(`Active user =${stats.activeUser} \n\nActive Bot =${stats.runingBot}`);
});


app.listen(app.get('port'), () => {
  console.log(`Example app listening on port ${app.get('port')}`);
});
