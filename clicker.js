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
  COIN_SWEEPER: ['M3', 'A1', 'A3', 'A8', 'A9', 'AI2'],
  BLUM: [],
  NOT_PIXEL: [],
  YESCOIN: [],
  POCKET_FI: [],
};
const disabledUserConfig = process.env.BOT_DISABLE_USERS || '';
const botDisabledU = disabledUserConfig ? JSON.parse(disabledUserConfig) : defaultDisabledUser;

const users1 = ['M1', 'Jio', 'M3', 'Super', 'AI2', 'AI3', 'AI4'];

const users2 = ['A1', 'A2', 'A3', 'A4', 'A5', 'A8', 'A9', 'A10'];

let activeUserBot1 = '';
let activeUserBot2 = '';
const getActiveUserBot = () => {
  return { activeUserBot1, activeUserBot2 };
};
const sleep = (ms) => {
  return new Promise((resolve) => setTimeout(resolve, ms));
};

const runPythonScript = (filename, user = '', timeout = 480000, action = '2', sessionDir = 'sessions') => {
  return new Promise(async (resolve, reject) => {
    try {
      const arguments = [filename, '-a', action, '-sd', sessionDir];
      if (user) {
        arguments.push('-u', user);
      }
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
const startBot = async () => {
  const sessionsDir = 'sessions-1';
  for (const iterator of Array.from({ length: 999999 })) {
    if (!isBotRuning) {
      isBotRuning = true;
      try {
        for (const user of users1) {
          if (botJsConfig['MMPRO'] && !(botDisabledU['MMPRO'] || []).includes(user)) {
            activeUserBot1 = `${user}====${'MMPRO'}`;
            var res = await runPythonScript('mainMMProBump.py', user, botJsConfig['MMPRO'], '2', sessionsDir);
            console.log('mainMMProBump 2 end res===', res);
          }
          if (botJsConfig['MOON_BIX'] && !(botDisabledU['MOON_BIX'] || []).includes(user)) {
            activeUserBot1 = `${user}====${'MOON_BIX'}`;
            var res = await runPythonScript(
              'mainMoonbix.py',
              user,
              botJsConfig['MOON_BIX'],
              '1',
              sessionsDir
            );
            console.log('mainMoonbix 4 end res===', res);
          }
          if (botJsConfig['MEMEFI'] && !(botDisabledU['MEMEFI'] || []).includes(user)) {
            activeUserBot1 = `${user}====${'MEMEFI'}`;
            var res = await runPythonScript('mainMemeFi.py', user, botJsConfig['MEMEFI'], '1', sessionsDir);
            console.log('mainMemeFi 5 end res===', res);
          }
          if (botJsConfig['COIN_SWEEPER'] && !(botDisabledU['COIN_SWEEPER'] || []).includes(user)) {
            activeUserBot1 = `${user}====${'COIN_SWEEPER'}`;
            var res = await runPythonScript(
              'mainCoinSweeper.py',
              user,
              botJsConfig['COIN_SWEEPER'],
              '1',
              sessionsDir
            );
            console.log('COIN_SWEEPER end res===', res);
          }
        }
        if (botJsConfig['POCKET_FI']) {
          activeUserBot1 = `ALL====${'POCKET_FI'}`;
          var res = await runPythonScript('mainPocketFi.py', '', botJsConfig['POCKET_FI'], '1', sessionsDir);
          console.log('POCKET_FI end res===', res);
        }
        if (botJsConfig['BLUM']) {
          activeUserBot1 = `ALL====${'BLUM'}`;
          var res = await runPythonScript('mainBlum.py', '', botJsConfig['BLUM'], '1', sessionsDir);
          console.log('mainBlum end res===', res);
        }
        if (botJsConfig['NOT_PIXEL']) {
          activeUserBot1 = `ALL====${'NOT_PIXEL'}`;
          var res = await runPythonScript('mainNotPixel.py', '', botJsConfig['NOT_PIXEL'], '1', sessionsDir);
          console.log('mainNotPixel end res===', res);
        }
        if (botJsConfig['YESCOIN']) {
          activeUserBot1 = `ALL====${'YESCOIN'}`;
          var res = await runPythonScript('mainYesCoin.py', '', botJsConfig['YESCOIN'], '2', sessionsDir);
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

let isBotRuning2 = false;
const startBot2 = async () => {
  const sessionsDir = 'sessions-2';
  for (const iterator of Array.from({ length: 999999 })) {
    if (!isBotRuning2) {
      isBotRuning2 = true;
      try {
        for (const user of users2) {
          if (botJsConfig['MMPRO'] && !(botDisabledU['MMPRO'] || []).includes(user)) {
            activeUserBot2 = `${user}====${'MMPRO'}`;
            var res = await runPythonScript('mainMMProBump.py', user, botJsConfig['MMPRO'], '2', sessionsDir);
            console.log('mainMMProBump 2 end res===', res);
          }
          if (botJsConfig['MOON_BIX'] && !(botDisabledU['MOON_BIX'] || []).includes(user)) {
            activeUserBot2 = `${user}====${'MOON_BIX'}`;
            var res = await runPythonScript(
              'mainMoonbix.py',
              user,
              botJsConfig['MOON_BIX'],
              '1',
              sessionsDir
            );
            console.log('mainMoonbix 4 end res===', res);
          }
          if (botJsConfig['MEMEFI'] && !(botDisabledU['MEMEFI'] || []).includes(user)) {
            activeUserBot2 = `${user}====${'MEMEFI'}`;
            var res = await runPythonScript('mainMemeFi.py', user, botJsConfig['MEMEFI'], '1', sessionsDir);
            console.log('mainMemeFi 5 end res===', res);
          }
          if (botJsConfig['COIN_SWEEPER'] && !(botDisabledU['COIN_SWEEPER'] || []).includes(user)) {
            activeUserBot2 = `${user}====${'COIN_SWEEPER'}`;
            var res = await runPythonScript(
              'mainCoinSweeper.py',
              user,
              botJsConfig['COIN_SWEEPER'],
              '1',
              sessionsDir
            );
            console.log('COIN_SWEEPER end res===', res);
          }
        }
        if (botJsConfig['POCKET_FI']) {
          activeUserBot2 = `ALL====${'POCKET_FI'}`;
          var res = await runPythonScript('mainPocketFi.py', '', botJsConfig['POCKET_FI'], '1', sessionsDir);
          console.log('POCKET_FI end res===', res);
        }
        if (botJsConfig['BLUM']) {
          activeUserBot2 = `ALL====${'BLUM'}`;
          var res = await runPythonScript('mainBlum.py', '', botJsConfig['BLUM'], '1', sessionsDir);
          console.log('mainBlum end res===', res);
        }
        if (botJsConfig['NOT_PIXEL']) {
          activeUserBot2 = `ALL====${'NOT_PIXEL'}`;
          var res = await runPythonScript('mainNotPixel.py', '', botJsConfig['NOT_PIXEL'], '1', sessionsDir);
          console.log('mainNotPixel end res===', res);
        }
        if (botJsConfig['YESCOIN']) {
          activeUserBot2 = `ALL====${'YESCOIN'}`;
          var res = await runPythonScript('mainYesCoin.py', '', botJsConfig['YESCOIN'], '2', sessionsDir);
          console.log('mainYesCoin 6 end res===', res);
        }
      } catch {
        isBotRuning2 = false;
      } finally {
        isBotRuning2 = false;
      }
    } else {
      await sleep(120000);
    }
  }
  console.log('stattaus===', isBotRuning2);
};
setTimeout(startBot2, 8 * 240000)
module.exports = { getActiveUserBot };
