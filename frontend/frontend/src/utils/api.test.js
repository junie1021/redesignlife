import assert from "node:assert/strict";
import test from "node:test";

test("builds an absolute API URL for the production backend", async () => {
  const api = await import("./api.js").catch(() => null);

  assert.ok(api, "API URL helper must exist");
  assert.equal(
    api.buildApiUrl(
      "/api/users/type-test",
      "https://example.ngrok-free.dev/",
    ),
    "https://example.ngrok-free.dev/api/users/type-test",
  );
});

test("uses the ngrok backend by default in a production build", async () => {
  const api = await import("./api.js").catch(() => null);

  assert.ok(api, "API URL helper must exist");
  assert.equal(
    api.resolveApiBaseUrl({ PROD: true }),
    "https://prognosis-thank-commotion.ngrok-free.dev",
  );
});

test("keeps local development requests relative for the Vite proxy", async () => {
  const api = await import("./api.js").catch(() => null);

  assert.ok(api, "API URL helper must exist");
  assert.equal(api.resolveApiBaseUrl({ DEV: true }), "");
});
