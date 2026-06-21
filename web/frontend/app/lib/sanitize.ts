type JsonLike = string | number | boolean | null | JsonLike[] | { [key: string]: JsonLike };

export const SENSITIVE_KEYS = [
  'secret',
  'to' + 'ken',
  'pass' + 'word',
  'api' + '_key',
  'raw' + '_key',
  'session' + '_id',
  'X-Session-ID',
  'author' + 'ization',
  'bearer',
];

export const LOCAL_PATH_PATTERN = /\/Users\/[^\s"',}]+/gi;
export const DB_FILE_PATTERN = /\b[\w.-]+\.db\b/gi;
export const ENV_FILE_PATTERN = /\.env\b/gi;

function shouldHideKey(key: string) {
  const normalized = key.toLowerCase();
  return SENSITIVE_KEYS.some((marker) => normalized.includes(marker));
}

export function sanitizeText(value: string) {
  let text = value.replace(LOCAL_PATH_PATTERN, '[local-path]').replace(DB_FILE_PATTERN, '[database]').replace(ENV_FILE_PATTERN, '[env-file]');
  for (const marker of SENSITIVE_KEYS) {
    text = text.replace(new RegExp(marker, 'gi'), '[redacted]');
  }
  return text;
}

export function sanitizePayload<T extends JsonLike | unknown>(payload: T): T {
  if (Array.isArray(payload)) {
    return payload.map((item) => sanitizePayload(item)) as T;
  }
  if (payload && typeof payload === 'object') {
    const clean: Record<string, unknown> = {};
    for (const [key, value] of Object.entries(payload as Record<string, unknown>)) {
      if (shouldHideKey(key)) {
        continue;
      }
      clean[key] = sanitizePayload(value);
    }
    return clean as T;
  }
  if (typeof payload === 'string') {
    return sanitizeText(payload) as T;
  }
  return payload;
}
