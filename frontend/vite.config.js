import { defineConfig } from 'vite';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export default defineConfig({
  plugins: [
    {
      name: 'copy-vanilla-assets',
      closeBundle() {
        const dist = path.resolve(__dirname, 'dist');
        if (fs.existsSync(dist)) {
          const appJsSrc = path.resolve(__dirname, 'app.js');
          const styleCssSrc = path.resolve(__dirname, 'style.css');
          if (fs.existsSync(appJsSrc)) {
            fs.copyFileSync(appJsSrc, path.join(dist, 'app.js'));
          }
          if (fs.existsSync(styleCssSrc)) {
            fs.copyFileSync(styleCssSrc, path.join(dist, 'style.css'));
          }
        }
      },
    },
  ],
});

