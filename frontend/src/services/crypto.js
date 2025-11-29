import CryptoJS from "crypto-js";

export function encryptMessage(base64Key, plaintext) {
  if (!base64Key) throw new Error("Missing AES key");
  const keyWA = CryptoJS.enc.Base64.parse(base64Key);
  const iv = CryptoJS.lib.WordArray.random(16);
  const encrypted = CryptoJS.AES.encrypt(plaintext, keyWA, {
    iv,
    mode: CryptoJS.mode.CBC,
    padding: CryptoJS.pad.Pkcs7,
  });
  const ivPlusCipher = iv.concat(encrypted.ciphertext);
  return CryptoJS.enc.Base64.stringify(ivPlusCipher);
}

export function decryptMessage(base64Key, b64IvCipher) {
  if (!base64Key) throw new Error("Missing AES key");
  if (!b64IvCipher) return null;
  const keyWA = CryptoJS.enc.Base64.parse(base64Key);
  const raw = CryptoJS.enc.Base64.parse(b64IvCipher);

  const iv = CryptoJS.lib.WordArray.create(raw.words.slice(0, 4), 16);
  const ciphertext = CryptoJS.lib.WordArray.create(raw.words.slice(4), raw.sigBytes - 16);

  const cipherParams = CryptoJS.lib.CipherParams.create({
    ciphertext: ciphertext,
  });

  const decrypted = CryptoJS.AES.decrypt(cipherParams, keyWA, {
    iv,
    mode: CryptoJS.mode.CBC,
    padding: CryptoJS.pad.Pkcs7,
  });

  return CryptoJS.enc.Utf8.stringify(decrypted);
}
