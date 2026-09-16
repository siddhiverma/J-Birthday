import fs from 'node:fs';
import crypto from 'node:crypto';
const [,,input,password]=process.argv;
if(!input||!password){console.error('Usage: node tools/encrypt-content.mjs content.json PASSWORD');process.exit(1)}
const salt=crypto.randomBytes(16),iv=crypto.randomBytes(12),key=crypto.pbkdf2Sync(password,salt,150000,32,'sha256');
const cipher=crypto.createCipheriv('aes-256-gcm',key,iv);const encrypted=Buffer.concat([cipher.update(fs.readFileSync(input)),cipher.final(),cipher.getAuthTag()]);
const payload={salt:salt.toString('base64'),iv:iv.toString('base64'),data:encrypted.toString('base64')};fs.writeFileSync('content.enc.js',`window.BIRTHDAY_PAYLOAD=${JSON.stringify(payload)};\n`);console.log('Wrote encrypted payload to content.enc.js');
