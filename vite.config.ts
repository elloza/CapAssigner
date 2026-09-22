import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';

// GitHub Pages serves the site from /<repo>/; override with BASE_PATH for other hosts.
export default defineConfig({
  base: process.env.BASE_PATH ?? '/CapAssigner/',
  plugins: [svelte()],
  worker: { format: 'es' },
  build: { target: 'es2022' },
});
