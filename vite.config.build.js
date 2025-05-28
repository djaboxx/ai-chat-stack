
  import { defineConfig } from 'vite';
  import react from '@vitejs/plugin-react';

  export default defineConfig({
    plugins: [react()],
    esbuild: {
      // Force esbuild for all transformations
      include: ['**/*.js', '**/*.ts', '**/*.jsx', '**/*.tsx'],
    },
    build: {
      // Use esbuild as the minifier
      minify: 'esbuild',
      rollupOptions: {
        // Skip platform-specific plugins
        external: [/@rollup\/rollup-.*/, /@rollup\/plugin-.*/]
      }
    },
    optimizeDeps: {
      // Force esbuild for dependency optimization
      force: true
    },
    resolve: {
      // Ensure proper resolution of modules
      dedupe: ['react', 'react-dom']
    }
  });
  