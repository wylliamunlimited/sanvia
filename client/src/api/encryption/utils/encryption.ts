export async function encryptAESGCM(plaintext: string, base64Key: string) {
  const key = await crypto.subtle.importKey(
    "raw",
    Uint8Array.from(atob(base64Key), (c) => c.charCodeAt(0)),
    "AES-GCM",
    false,
    ["encrypt"]
  );
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const encoded = new TextEncoder().encode(plaintext);
  const encrypted = await crypto.subtle.encrypt(
    { name: "AES-GCM", iv },
    key,
    encoded
  );
  return {
    ciphertext: btoa(String.fromCharCode(...new Uint8Array(encrypted))),
    iv: btoa(String.fromCharCode(...iv)),
  };
}

export async function decryptAESGCM(
  ciphertextB64: string,
  ivB64: string,
  base64Key: string
): Promise<string> {
  const key = await crypto.subtle.importKey(
    "raw",
    Uint8Array.from(atob(base64Key), (c) => c.charCodeAt(0)),
    "AES-GCM",
    false,
    ["decrypt"]
  );
  const ciphertext = Uint8Array.from(atob(ciphertextB64), (c) =>
    c.charCodeAt(0)
  );
  const iv = Uint8Array.from(atob(ivB64), (c) => c.charCodeAt(0));
  const decrypted = await crypto.subtle.decrypt(
    { name: "AES-GCM", iv },
    key,
    ciphertext
  );
  return new TextDecoder().decode(decrypted);
}
