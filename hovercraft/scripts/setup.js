/**
 * [사용자] Operator Hub 통합 환경 자율 설치 스크립트 (Encapsulated Edition) 
 * 위치: hovercraft/scripts/setup.js
 * 이 스크립트는 상위 MCP 루트를 자동 감지하여 모든 환경을 구축합니다. 
 */
const { execSync, exec } = require('child_process');
const fs = require('fs');
const path = require('path');

// [사용자] 현재 위치(hovercraft/scripts) 기준 두 단계 위가 진짜 프로젝트 루트입니다. 
const rootDir = path.join(__dirname, '..', '..');
const webDir = path.join(rootDir, 'hovercraft');
const venvDir = path.join(rootDir, '.venv');
const isWindows = process.platform === 'win32';

console.log('\n [OPERATOR-GENESIS] 통합 지휘소 환경 구축을 시작합니다... ');

function openBrowser(url) {
  const start = isWindows ? 'start' : 'open';
  exec(`${start} ${url}`);
}

function tryCommand(cmd) {
  try {
    execSync(cmd, { stdio: 'ignore' });
    return true;
  } catch (e) {
    return false;
  }
}

// 1. Node.js 확보
function ensureNode() {
  const currentVersion = process.version.match(/^v(\d+)\./)[1];
  if (parseInt(currentVersion) < 18) {
    console.log(` Node.js 버전이 낮습니다 (현재: ${process.version}). 설치를 시도합니다...`);
    if (isWindows) {
      if (tryCommand('winget --version')) {
        execSync('winget install OpenJS.NodeJS.LTS --silent --accept-package-agreements', { stdio: 'inherit' });
      } else {
        openBrowser('https://nodejs.org/en/download/');
        throw new Error('Node.js 수동 설치가 필요합니다.');
      }
    } else {
      if (tryCommand('brew --version')) {
        execSync('brew install node', { stdio: 'inherit' });
      } else {
        openBrowser('https://nodejs.org/en/download/');
        throw new Error('Homebrew 설치 혹은 Node.js 수동 설치가 필요합니다.');
      }
    }
  } else {
    console.log(` Node.js 환경 확인됨: ${process.version}`);
  }
}

// 2. Python 확보
function ensurePython() {
  const pyCmd = isWindows ? 'python' : 'python3';
  if (!tryCommand(`${pyCmd} --version`)) {
    console.log(' Python 3가 발견되지 않았습니다. 즉시 설치를 시도합니다...');
    if (isWindows) {
      if (tryCommand('winget --version')) {
        execSync('winget install Python.Python.3.12 --silent --accept-package-agreements', { stdio: 'inherit' });
      } else {
        openBrowser('https://www.python.org/downloads/');
        throw new Error('Python 3 수동 설치가 필요합니다.');
      }
    } else {
      if (tryCommand('brew --version')) {
        execSync('brew install python@3.12', { stdio: 'inherit' });
      } else {
        openBrowser('https://www.python.org/downloads/');
        throw new Error('Python 3 수동 설치가 필요합니다.');
      }
    }
  } else {
    console.log(` Python 환경 확인됨: ${pyCmd}`);
  }
}

try {
  ensureNode();
  ensurePython();

  const pyCmd = isWindows ? 'python' : 'python3';

  // [사용자] 이제 자기 자신(hovercraft) 안에서 npm install을 수행합니다.  (에러를 확인할 수 있도록 --silent 제거)
  console.log('\n [1/3] 웹 프론트엔드 패키지 동기화 중...');
  execSync('npm install --no-audit --no-fund', { cwd: webDir, stdio: 'inherit' });

  console.log('\n [2/3] 파이썬 가상환경(.venv) 무결성 점검...');
  if (!fs.existsSync(venvDir)) {
    execSync(`${pyCmd} -m venv .venv`, { cwd: rootDir, stdio: 'inherit' });
  }

  console.log('\n [3/3] 백엔드 규약 패키지(requirements.txt) 자동 설치...');
  const pythonPath = isWindows 
    ? path.join(venvDir, 'Scripts', 'python.exe') 
    : path.join(venvDir, 'bin', 'python');
  
  execSync(`"${pythonPath}" -m pip install --upgrade pip --quiet`, { cwd: rootDir, stdio: 'inherit' });
  execSync(`"${pythonPath}" -m pip install -r requirements.txt --quiet`, { cwd: rootDir, stdio: 'inherit' });

  console.log('\n [SUCCESS] 모든 지휘 계통이 자율적으로 구축되었습니다! \n');

} catch (error) {
  console.error('\n [AUTONOMOUS ERROR] 구축 중단:');
  console.error(`   > ${error.message}\n`);
  process.exit(1);
}
