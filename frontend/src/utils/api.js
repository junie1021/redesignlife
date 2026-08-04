const productionApiBaseUrl = "https://redesignlife-backend.vercel.app";

// Selects an override when configured and the hosted backend in production.
export function resolveApiBaseUrl(env = import.meta.env) {
  const configuredBaseUrl = env?.VITE_API_BASE_URL?.trim();

  if (configuredBaseUrl) {
    return configuredBaseUrl.replace(/\/+$/, "");
  }

  return env?.PROD ? productionApiBaseUrl : "";
}

const configuredApiBaseUrl = resolveApiBaseUrl();

// Builds an API URL that is absolute in production and relative in local development.
export function buildApiUrl(path, baseUrl = configuredApiBaseUrl) {
  const normalizedBaseUrl = baseUrl.trim().replace(/\/+$/, "");
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;

  return `${normalizedBaseUrl}${normalizedPath}`;
}
