// Strato.de Deployment Configuration
// PM2 Ecosystem for Kameleon.life Production

module.exports = {
  apps: [
    {
      name: 'kameleon-frontend',
      script: 'node_modules/.bin/next',
      args: 'start -p 80',
      cwd: '/var/www/kameleon.life',
      instances: 1,
      exec_mode: 'cluster',
      watch: false,
      max_memory_restart: '1G',
      env: {
        NODE_ENV: 'production',
        PORT: 80
      },
      error_file: '/var/log/pm2/kameleon-frontend.error.log',
      out_file: '/var/log/pm2/kameleon-frontend.out.log',
      log_file: '/var/log/pm2/kameleon-frontend.log'
    },
    {
      name: 'asi-backend',
      script: 'python',
      args: '-m uvicorn app.main:app --host 0.0.0.0 --port 8080',
      cwd: '/var/www/kameleon.life/ultracom',
      instances: 1,
      exec_mode: 'fork',
      watch: false,
      max_memory_restart: '512M',
      env: {
        PYTHONPATH: '/var/www/kameleon.life/ultracom',
        ENVIRONMENT: 'production'
      },
      error_file: '/var/log/pm2/asi-backend.error.log',
      out_file: '/var/log/pm2/asi-backend.out.log',
      log_file: '/var/log/pm2/asi-backend.log'
    },
    {
      name: 'neurosonix-api',
      script: 'python',
      args: '-m uvicorn neurosonix_server:app --host 0.0.0.0 --port 8081',
      cwd: '/var/www/kameleon.life/ultracom',
      instances: 1,
      exec_mode: 'fork',
      watch: false,
      max_memory_restart: '512M',
      env: {
        PYTHONPATH: '/var/www/kameleon.life/ultracom',
        ENVIRONMENT: 'production'
      },
      error_file: '/var/log/pm2/neurosonix-api.error.log',
      out_file: '/var/log/pm2/neurosonix-api.out.log',
      log_file: '/var/log/pm2/neurosonix-api.log'
    }
  ]
};
