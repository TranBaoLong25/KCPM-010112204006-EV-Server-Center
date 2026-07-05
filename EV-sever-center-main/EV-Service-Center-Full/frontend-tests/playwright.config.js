module.exports = {
  testDir: "./tests",
  reporter: "html",
  use: {
    baseURL: "http://localhost",
    headless: false,
    screenshot: "only-on-failure",
    video: "retain-on-failure",
  },
};
