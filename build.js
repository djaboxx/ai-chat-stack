// Custom build script to handle rollup architecture issues
import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';

// Ensure proper environment variables are set
process.env.ROLLUP_SKIP_PLUGINS = 'true';
process.env.VITE_FORCE_ESBUILD = 'true'; // Force Vite to use esbuild

console.log('🚀 Starting custom build process...');

try {
  // Check if we're in a Docker environment
  const inDocker = fs.existsSync('/.dockerenv');
  console.log(`Running in Docker: ${inDocker ? 'Yes' : 'No'}`);

  // Add NODE_OPTIONS if in Docker
  if (inDocker) {
    process.env.NODE_OPTIONS = '--max-old-space-size=4096';
  }

  console.log('Checking for build approach...');
  
  // Determine whether to use esbuild or vite based on the environment
  if (inDocker || process.env.USE_ESBUILD === 'true') {
    console.log('Using direct esbuild for build process (bypassing rollup)...');
    
    try {
      // Ensure we're using the correct esbuild binary
      console.log('Running esbuild build script with proper binary path...');
      // Make sure ESBUILD_BINARY_PATH environment variable is set
      if (!process.env.ESBUILD_BINARY_PATH) {
        process.env.ESBUILD_BINARY_PATH = path.join(process.cwd(), 'node_modules/esbuild/bin/esbuild');
        console.log(`Set ESBUILD_BINARY_PATH to: ${process.env.ESBUILD_BINARY_PATH}`);
      }
      
      execSync('node esbuild.config.js', {
        stdio: 'inherit',
        env: process.env
      });
    } catch (esbuildError) {
      console.error('esbuild direct build failed, falling back to vite:', esbuildError.message);
      // Fall back to Vite with custom config if esbuild fails
      useViteBuild();
    }
  } else {
    // Use Vite with custom config for non-Docker environments
    useViteBuild();
  }
  
  console.log('✅ Build completed successfully!');
  process.exit(0);
} catch (error) {
  console.error('❌ Build failed:', error.message);
  process.exit(1);
}

function useViteBuild() {
  // Create a custom Vite config file for the build
  const tempViteConfigPath = path.join(process.cwd(), 'vite.config.build.js');
  
  // Write a temporary Vite config that forces esbuild
  const viteConfigContent = `
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
        external: [/@rollup\\/rollup-.*/, /@rollup\\/plugin-.*/]
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
  `;

  fs.writeFileSync(tempViteConfigPath, viteConfigContent);
  console.log('Created temporary Vite config for build');

  // Run Vite build with the custom config
  console.log('Building with Vite using esbuild...');
  execSync(`node ./node_modules/vite/bin/vite.js build --config vite.config.build.js`, { 
    stdio: 'inherit',
    env: process.env
  });
  
  // Clean up temporary config
  fs.unlinkSync(tempViteConfigPath);
}
