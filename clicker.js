const { spawn } = require('child_process');
const envFile = '.env';
require('dotenv').config({ path: envFile });

const users = process.env.USER_NAMES
  ? process.env.USER_NAMES.split(',')
  : [
      'Manish-dalal',
      'Jio',
      'M3',
      'A1',
      'A2',
      'A3',
      'A4',
      'A5',
      'Super',
      'A8',
      'A9',
      'A10',
      'AI2',
      'AI3',
      'AI4',
    ];

const sleep = (ms) => {
  return new Promise((resolve) => setTimeout(resolve, ms));
};

const runPythonScript = (filename, user = '', timeout = 240000) => {
  return new Promise(async (resolve, reject) => {
    try {
      const arguments = user ? [filename, '-a', '2', '-u', user] : [filename, '-a', '2'];
      const python = spawn('python', arguments);
      const timeoutRf = setTimeout(() => {
        python.kill();
        console.log(`python.kill calll`, filename);
        return resolve({});
      }, timeout);
      var scriptOutput = '';
      // collect data from script
      python.stdout.setEncoding('utf8');
      python.stdout.on('data', function (data) {
        // data = data.toString();
        console.log('PS=', data);
        scriptOutput += data;
      });

      python.stderr.setEncoding('utf8');
      python.stderr.on('data', function (data) {
        console.log('stderr: ' + data);
        data = data.toString();
        scriptOutput += data;
      });
      // in close event we are sure that stream is from child process is closed
      python.on('close', function (code) {
        console.log('code', code);
        clearTimeout(timeoutRf);
        return resolve({});
      });

      python.on('error', (error) => {
        console.log(`child process error`, error);
        clearTimeout(timeoutRf);
        return resolve({});
      });
    } catch (error) {
      return resolve({});
    }
  });
};

let isBotRuning = false;
const clicker = async () => {
  if (!isBotRuning) {
    isBotRuning = true;
    try {
      for (const user of users) {
        if (!process.env.DISABLE_BLUM) {
          var res = await runPythonScript('mainBlum.py', user, 100000);
          console.log('mainBlum 1 end res===', res);
        }
        if (!process.env.DISABLE_MMPRO) {
          var res = await runPythonScript('mainMMProBump.py', user, 60000);
          console.log('mainMMProBump 2 end res===', res);
        }
        if (!process.env.DISABLE_X_EMPIRE) {
          var res = await runPythonScript('mainXEmpire.py', user, 120000);
          console.log('mainXEmpire 3 end res===', res);
        }
        if (!process.env.DISABLE_MOON_BIX) {
          var res = await runPythonScript('mainMoonbix.py', user, 360000);
          console.log('mainMoonbix 4 end res===', res);
        }
      }
      if (!process.env.DISABLE_MEMEFI) {
        var res = await runPythonScript('mainMemeFi.py');
        console.log('mainMemeFi 5 end res===', res);
      }
      if (!process.env.DISABLE_YESCOIN) {
        var res = await runPythonScript('mainYesCoin.py');
        console.log('mainYesCoin 6 end res===', res);
      }
    } finally {
      isBotRuning = false;
    }
    return true;
  }
  return true;
};
const startBot = async () => {
  for (const iterator of Array.from({ length: 999999 })) {
    if (!isBotRuning) {
      isBotRuning = true;
      try {
        for (const user of users) {
          if (!process.env.DISABLE_BLUM) {
            var res = await runPythonScript('mainBlum.py', user, 100000);
            console.log('mainBlum 1 end res===', res);
          }
          if (!process.env.DISABLE_MMPRO) {
            var res = await runPythonScript('mainMMProBump.py', user, 60000);
            console.log('mainMMProBump 2 end res===', res);
          }
          if (!process.env.DISABLE_X_EMPIRE) {
            var res = await runPythonScript('mainXEmpire.py', user, 120000);
            console.log('mainXEmpire 3 end res===', res);
          }
          if (!process.env.DISABLE_MOON_BIX) {
            var res = await runPythonScript('mainMoonbix.py', user, 360000);
            console.log('mainMoonbix 4 end res===', res);
          }
        }
        if (!process.env.DISABLE_MEMEFI) {
          var res = await runPythonScript('mainMemeFi.py');
          console.log('mainMemeFi 5 end res===', res);
        }
        if (!process.env.DISABLE_YESCOIN) {
          var res = await runPythonScript('mainYesCoin.py');
          console.log('mainYesCoin 6 end res===', res);
        }
      } finally {
        isBotRuning = false;
      }
    } else {
      await sleep(120000);
    }
  }
  console.log('stattaus===', isBotRuning);
};
startBot();
module.exports = { clicker };
