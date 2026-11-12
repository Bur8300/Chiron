import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "../tests/frontend/browser",
  tsconfig: "../tests/frontend/tsconfig.json",
  testMatch: "**/*.browser.ts",
  timeout: 120_000,
  outputDir: "../tests/frontend/browser-results",
  reporter: "list",
  use: {
    baseURL: "http://127.0.0.1:4173",
    browserName: "chromium",
    launchOptions: {
      executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH,
    },
    trace: "retain-on-failure",
  },
  webServer: {
    command: "npm run dev -- --host 127.0.0.1 --port 4173 --strictPort",
    url: "http://127.0.0.1:4173",
    reuseExistingServer: false,
  },
});
