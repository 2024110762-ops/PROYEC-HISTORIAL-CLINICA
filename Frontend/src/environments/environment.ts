const apiUrl = (globalThis as { HCE_API_URL?: string }).HCE_API_URL ?? 'http://127.0.0.1:8000';

export const environment = {
  production: false,
  apiUrl,
};
