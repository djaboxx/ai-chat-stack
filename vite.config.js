// vite.config.js
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    minify: 'esbuild',
    rollupOptions: {
      // Explicitly bypass platform-specific rollup plugins
      external: [/@rollup\/rollup-.*/, /@rollup\/plugin-.*/],
    },
  },
  esbuild: {
    // Force esbuild for all transformations
    include: ['**/*.js', '**/*.ts', '**/*.jsx', '**/*.tsx'],
  },
  define: {
    // Define environment variables
    'process.env.ROLLUP_SKIP_PLUGINS': JSON.stringify('true'),
    'process.env.VITE_FORCE_ESBUILD': JSON.stringify('true'),
  },
  optimizeDeps: {
    // Force esbuild for dependency optimization
    force: true
  }
});
