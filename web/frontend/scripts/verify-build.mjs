import { existsSync } from 'node:fs';

const pages = ['login', 'dashboard', 'strategy', 'reports', 'risk', 'settings', 'admin', 'api-docs'];
const missing = pages.filter((page) => !existsSync(`app/${page}/page.tsx`));

if (missing.length > 0) {
  console.error(`Missing pages: ${missing.join(', ')}`);
  process.exit(1);
}

console.log('V3.2 frontend structure verified');
