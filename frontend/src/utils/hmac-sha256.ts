/**
 * SHA-256 / HMAC-SHA256 工具。
 *
 * 优先使用浏览器原生 WebCrypto（`crypto.subtle`，仅在安全上下文可用：HTTPS 或 localhost）。
 * 非安全上下文（如 HTTP + 局域网 IP）下 `crypto.subtle` 为 `undefined`，
 * 此时回退到下方纯 JS 实现的 SHA-256，保证签名计算在任何环境下都能进行。
 *
 * 纯 JS 实现为标准 SHA-256（FIPS 180-4），输出与原生 WebCrypto 完全一致——
 * 这里只是与后端契约对齐签名，不承担机密性边界（机密性由 app_secret 本身保证）。
 */

function hasSubtleCrypto(): boolean {
  return typeof crypto !== 'undefined' && Boolean(crypto.subtle);
}

// ---- 纯 JS SHA-256（仅作回退，逻辑等价于标准算法）----

const K = new Uint32Array([
  0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5, 0xd807aa98,
  0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786,
  0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da, 0x983e5152, 0xa831c66d, 0xb00327c8,
  0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
  0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85, 0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819,
  0xd6990624, 0xf40e3585, 0x106aa070, 0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a,
  0x5b9cca4f, 0x682e6ff3, 0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
]);

const BLOCK_SIZE = 64;

function rotr(x: number, n: number): number {
  return (x >>> n) | (x << (32 - n));
}

/** 计算一段 UTF-8 字节的 SHA-256，返回 32 字节摘要 */
export function sha256Bytes(msg: Uint8Array): Uint8Array {
  const l = msg.length;
  const bitLen = l * 8;
  // 补位：0x80 + 0x00 + 8 字节大端比特长度，总长度为 64 的倍数
  const paddedLen = Math.ceil((l + 1 + 8) / 64) * 64;
  const data = new Uint8Array(paddedLen);
  data.set(msg);
  data[l] = 0x80;
  const dv = new DataView(data.buffer);
  dv.setUint32(paddedLen - 8, Math.floor(bitLen / 0x100000000));
  dv.setUint32(paddedLen - 4, bitLen >>> 0);

  const H = new Uint32Array([
    0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19
  ]);
  const W = new Uint32Array(64);

  for (let offset = 0; offset < paddedLen; offset += BLOCK_SIZE) {
    for (let i = 0; i < 16; i++) {
      W[i] = dv.getUint32(offset + i * 4);
    }
    for (let i = 16; i < 64; i++) {
      const s0 = rotr(W[i - 15], 7) ^ rotr(W[i - 15], 18) ^ (W[i - 15] >>> 3);
      const s1 = rotr(W[i - 2], 17) ^ rotr(W[i - 2], 19) ^ (W[i - 2] >>> 10);
      W[i] = (W[i - 16] + s0 + W[i - 7] + s1) >>> 0;
    }

    let a = H[0];
    let b = H[1];
    let c = H[2];
    let d = H[3];
    let e = H[4];
    let f = H[5];
    let g = H[6];
    let h = H[7];

    for (let i = 0; i < 64; i++) {
      const S1 = rotr(e, 6) ^ rotr(e, 11) ^ rotr(e, 25);
      const ch = (e & f) ^ (~e & g);
      const t1 = (h + S1 + ch + K[i] + W[i]) >>> 0;
      const S0 = rotr(a, 2) ^ rotr(a, 13) ^ rotr(a, 22);
      const maj = (a & b) ^ (a & c) ^ (b & c);
      const t2 = (S0 + maj) >>> 0;
      h = g;
      g = f;
      f = e;
      e = (d + t1) >>> 0;
      d = c;
      c = b;
      b = a;
      a = (t1 + t2) >>> 0;
    }

    H[0] = (H[0] + a) >>> 0;
    H[1] = (H[1] + b) >>> 0;
    H[2] = (H[2] + c) >>> 0;
    H[3] = (H[3] + d) >>> 0;
    H[4] = (H[4] + e) >>> 0;
    H[5] = (H[5] + f) >>> 0;
    H[6] = (H[6] + g) >>> 0;
    H[7] = (H[7] + h) >>> 0;
  }

  const out = new Uint8Array(32);
  const odv = new DataView(out.buffer);
  for (let i = 0; i < 8; i++) odv.setUint32(i * 4, H[i]);
  return out;
}

/** HMAC-SHA256(key, msg)，返回 32 字节 */
export function hmacSha256Bytes(key: Uint8Array, msg: Uint8Array): Uint8Array {
  let k = key;
  if (k.length > BLOCK_SIZE) k = sha256Bytes(k);
  if (k.length < BLOCK_SIZE) {
    const padded = new Uint8Array(BLOCK_SIZE);
    padded.set(k);
    k = padded;
  }
  const ipad = new Uint8Array(BLOCK_SIZE);
  const opad = new Uint8Array(BLOCK_SIZE);
  for (let i = 0; i < BLOCK_SIZE; i++) {
    ipad[i] = k[i] ^ 0x36;
    opad[i] = k[i] ^ 0x5c;
  }
  const inner = new Uint8Array(BLOCK_SIZE + msg.length);
  inner.set(ipad);
  inner.set(msg, BLOCK_SIZE);
  const innerHash = sha256Bytes(inner);
  const outer = new Uint8Array(BLOCK_SIZE + innerHash.length);
  outer.set(opad);
  outer.set(innerHash, BLOCK_SIZE);
  return sha256Bytes(outer);
}

function toHex(bytes: Uint8Array): string {
  return Array.from(bytes)
    .map(b => b.toString(16).padStart(2, '0'))
    .join('');
}

/**
 * 计算 text 的 SHA-256，返回小写 hex。
 * 安全上下文下用原生 WebCrypto，否则回退纯 JS。
 */
export async function sha256Hex(text: string): Promise<string> {
  const data = new TextEncoder().encode(text);
  if (hasSubtleCrypto()) {
    const digest = await crypto.subtle.digest('SHA-256', data);
    return toHex(new Uint8Array(digest));
  }
  return toHex(sha256Bytes(data));
}

/**
 * HMAC-SHA256(secret, message)，返回小写 hex。
 * 安全上下文下用原生 WebCrypto，否则回退纯 JS。
 */
export async function hmacSha256Hex(secret: string, message: string): Promise<string> {
  const enc = new TextEncoder();
  if (hasSubtleCrypto()) {
    const key = await crypto.subtle.importKey('raw', enc.encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, [
      'sign'
    ]);
    const sig = await crypto.subtle.sign('HMAC', key, enc.encode(message));
    return toHex(new Uint8Array(sig));
  }
  return toHex(hmacSha256Bytes(enc.encode(secret), enc.encode(message)));
}
