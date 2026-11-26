const apiUrl = (globalThis as { HCE_API_URL?: string }).HCE_API_URL ?? '';

export const environment = {
  production: true,
  apiUrl,
};
