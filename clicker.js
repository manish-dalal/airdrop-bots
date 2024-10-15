const botConfig = require('./botConfig.json');
const { spawn } = require('child_process');
const envFile = '.env';
require('dotenv').config({ path: envFile });

const stringifyConfig = process.env.BOT_CONFIG || '';
const botJsConfig = stringifyConfig ? JSON.parse(stringifyConfig) : botConfig;

const defaultDisabledUser = {
  MMPRO: [],
  MOON_BIX: [],
  MEMEFI: [],
  COIN_SWEEPER: ['M3', 'A1', 'A3', 'A8', 'A9', 'AAI2', 'AI2'],
  BLUM: [],
  NOT_PIXEL: [],
  YESCOIN: [],
  POCKET_FI: [],
};
const disabledUserConfig = process.env.BOT_DISABLE_USERS || '';
const botDisabledU = disabledUserConfig ? JSON.parse(disabledUserConfig) : defaultDisabledUser;

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
      'A7',
      'A8',
      'A9',
      'A10',
      'AI2',
      'AI3',
      'AI4',
    ];

let activeUserBot = '';
const getActiveUserBot = () => {
  const [activeUser = '', runingBot = ''] = activeUserBot.split('====');
  return { activeUser, runingBot };
};
const sleep = (ms) => {
  return new Promise((resolve) => setTimeout(resolve, ms));
};

const runPythonScript = (filename, user = '', timeout = 480000, action = '2') => {
  return new Promise(async (resolve, reject) => {
    try {
      const arguments = user ? [filename, '-a', action, '-u', user] : [filename, '-a', action];
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
        if (botJsConfig['MMPRO'] && !(botDisabledU['MMPRO'] || []).includes(user)) {
          activeUserBot = `${user}====${'MMPRO'}`;
          var res = await runPythonScript('mainMMProBump.py', user, botJsConfig['MMPRO']);
          console.log('mainMMProBump 2 end res===', res);
        }
        if (botJsConfig['MOON_BIX'] && !(botDisabledU['MOON_BIX'] || []).includes(user)) {
          activeUserBot = `${user}====${'MOON_BIX'}`;
          var res = await runPythonScript('mainMoonbix.py', user, botJsConfig['MOON_BIX'], '1');
          console.log('mainMoonbix 4 end res===', res);
        }
        if (botJsConfig['MEMEFI'] && !(botDisabledU['MEMEFI'] || []).includes(user)) {
          activeUserBot = `${user}====${'MEMEFI'}`;
          var res = await runPythonScript('mainMemeFi.py', user, botJsConfig['MEMEFI'], '1');
          console.log('mainMemeFi 5 end res===', res);
        }
        if (botJsConfig['COIN_SWEEPER'] && !(botDisabledU['COIN_SWEEPER'] || []).includes(user)) {
          activeUserBot = `${user}====${'COIN_SWEEPER'}`;
          var res = await runPythonScript('mainCoinSweeper.py', user, botJsConfig['COIN_SWEEPER'], '1');
          console.log('COIN_SWEEPER end res===', res);
        }
      }
      if (botJsConfig['POCKET_FI']) {
        activeUserBot = `ALL====${'POCKET_FI'}`;
        var res = await runPythonScript('mainPocketFi.py', '', botJsConfig['POCKET_FI'], '1');
        console.log('POCKET_FI end res===', res);
      }
      if (botJsConfig['BLUM']) {
        activeUserBot = `ALL====${'BLUM'}`;
        var res = await runPythonScript('mainBlum.py', '', botJsConfig['BLUM'], '1');
        console.log('mainBlum end res===', res);
      }
      if (botJsConfig['NOT_PIXEL']) {
        activeUserBot = `ALL====${'NOT_PIXEL'}`;
        var res = await runPythonScript('mainNotPixel.py', '', botJsConfig['NOT_PIXEL'], '1');
        console.log('mainNotPixel end res===', res);
      }
      if (botJsConfig['YESCOIN']) {
        activeUserBot = `ALL====${'YESCOIN'}`;
        var res = await runPythonScript('mainYesCoin.py', '', botJsConfig['YESCOIN']);
        console.log('mainYesCoin 6 end res===', res);
      }
    } catch {
      isBotRuning = false;
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
          if (botJsConfig['MMPRO'] && !(botDisabledU['MMPRO'] || []).includes(user)) {
            activeUserBot = `${user}====${'MMPRO'}`;
            var res = await runPythonScript('mainMMProBump.py', user, botJsConfig['MMPRO']);
            console.log('mainMMProBump 2 end res===', res);
          }
          if (botJsConfig['MOON_BIX'] && !(botDisabledU['MOON_BIX'] || []).includes(user)) {
            activeUserBot = `${user}====${'MOON_BIX'}`;
            var res = await runPythonScript('mainMoonbix.py', user, botJsConfig['MOON_BIX'], '1');
            console.log('mainMoonbix 4 end res===', res);
          }
          if (botJsConfig['MEMEFI'] && !(botDisabledU['MEMEFI'] || []).includes(user)) {
            activeUserBot = `${user}====${'MEMEFI'}`;
            var res = await runPythonScript('mainMemeFi.py', user, botJsConfig['MEMEFI'], '1');
            console.log('mainMemeFi 5 end res===', res);
          }
          if (botJsConfig['COIN_SWEEPER'] && !(botDisabledU['COIN_SWEEPER'] || []).includes(user)) {
            activeUserBot = `${user}====${'COIN_SWEEPER'}`;
            var res = await runPythonScript('mainCoinSweeper.py', user, botJsConfig['COIN_SWEEPER'], '1');
            console.log('COIN_SWEEPER end res===', res);
          }
        }
        if (botJsConfig['POCKET_FI']) {
          activeUserBot = `ALL====${'POCKET_FI'}`;
          var res = await runPythonScript('mainPocketFi.py', '', botJsConfig['POCKET_FI'], '1');
          console.log('POCKET_FI end res===', res);
        }
        if (botJsConfig['BLUM']) {
          activeUserBot = `ALL====${'BLUM'}`;
          var res = await runPythonScript('mainBlum.py', '', botJsConfig['BLUM'], '1');
          console.log('mainBlum end res===', res);
        }
        if (botJsConfig['NOT_PIXEL']) {
          activeUserBot = `ALL====${'NOT_PIXEL'}`;
          var res = await runPythonScript('mainNotPixel.py', '', botJsConfig['NOT_PIXEL'], '1');
          console.log('mainNotPixel end res===', res);
        }
        if (botJsConfig['YESCOIN']) {
          activeUserBot = `ALL====${'YESCOIN'}`;
          var res = await runPythonScript('mainYesCoin.py', '', botJsConfig['YESCOIN']);
          console.log('mainYesCoin 6 end res===', res);
        }
      } catch {
        isBotRuning = false;
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
module.exports = { clicker, getActiveUserBot };
