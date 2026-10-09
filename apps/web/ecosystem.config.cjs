module.exports = {
  apps: [
    {
      name: "clisonix-web",
      cwd: "/app",
      script: "node_modules/next/dist/bin/next",
      args: "start -H 0.0.0.0 -p 3000",
      exec_mode: "cluster",
      instances: "max",
      autorestart: true,
      max_memory_restart: "1G",
      listen_timeout: 10000,
      kill_timeout: 5000,
      env: {
        NODE_ENV: "production",
        PORT: "3000",
      },
    },
  ],
};
