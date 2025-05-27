// esbuild.config.js
// Direct build approach using esbuild to avoid rollup architecture issues
import { build } from 'esbuild';
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import { execSync } from 'child_process';

// Log esbuild version for debugging
try {
  console.log('esbuild version:', execSync('npx esbuild --version').toString().trim());
  console.log('Node.js version:', process.version);
  console.log('ESBUILD_BINARY_PATH:', process.env.ESBUILD_BINARY_PATH || 'not set');
} catch (e) {
  console.warn('Could not determine esbuild version:', e.message);
}

const __dirname = path.dirname(fileURLToPath(import.meta.url));

console.log('🚀 Starting esbuild direct build process...');

// Make sure the dist directory exists
async function ensureDir(dir) {
  try {
    await fs.mkdir(dir, { recursive: true });
  } catch (e) {
    if (e.code !== 'EEXIST') throw e;
  }
}

// Copy and process index.html
async function processHtml() {
  console.log('Processing HTML...');
  try {
    const html = await fs.readFile('index.html', 'utf8');
    // Replace development paths with production paths
    const processedHtml = html
      .replace(/src="[\./]*src\/main.tsx"/, 'src="/assets/index.js"')
      .replace(/type="module"/, '');
    
    await ensureDir('dist');
    await ensureDir('dist/assets');
    
    await fs.writeFile('dist/index.html', processedHtml);
    console.log('✅ HTML processed');
  } catch (error) {
    console.error('❌ HTML processing failed:', error.message);
    throw error;
  }
}

// Copy public assets if they exist
async function copyPublicAssets() {
  console.log('Copying public assets...');
  try {
    try {
      const files = await fs.readdir('public');
      
      for (const file of files) {
        const srcPath = path.join('public', file);
        const destPath = path.join('dist', file);
        const stat = await fs.stat(srcPath);
        
        if (stat.isFile()) {
          await fs.copyFile(srcPath, destPath);
        } else if (stat.isDirectory()) {
          await ensureDir(destPath);
          // Copy directory recursively (simplified for this example)
          // Would need deeper implementation for production
        }
      }
      console.log('✅ Public assets copied');
    } catch (e) {
      if (e.code !== 'ENOENT') throw e;
      console.log('⚠️ No public folder found, skipping assets copy');
    }
  } catch (error) {
    console.error('❌ Assets copying failed:', error.message);
    throw error;
  }
}

// Copy CSS files
async function copyCssFiles() {
  console.log('Copying CSS files...');
  try {
    const cssFiles = [
      'markdown-styles.css',
      'syntax-highlight.css'
    ];
    
    for (const file of cssFiles) {
      try {
        const cssContent = await fs.readFile(file, 'utf8');
        await fs.writeFile(path.join('dist/assets', file), cssContent);
      } catch (e) {
        if (e.code !== 'ENOENT') throw e;
        console.log(`⚠️ CSS file ${file} not found, skipping`);
      }
    }
    console.log('✅ CSS files copied');
  } catch (error) {
    console.error('❌ CSS copying failed:', error.message);
    throw error;
  }
}

// Main build function
async function runBuild() {
  try {
    // Find the entry point - could be in src/main.tsx or at the root
    let entryPoint;
    try {
      await fs.access('src/main.tsx');
      entryPoint = 'src/main.tsx';
    } catch {
      try {
        await fs.access('main.tsx');
        entryPoint = 'main.tsx';
      } catch {
        try {
          await fs.access('index.tsx');
          entryPoint = 'index.tsx';
        } catch {
          throw new Error('Could not find entry point (main.tsx or index.tsx)');
        }
      }
    }
    
    console.log(`Using entry point: ${entryPoint}`);
    
    // Build with esbuild
    await build({
      entryPoints: [entryPoint],
      bundle: true,
      minify: true,
      outfile: 'dist/assets/index.js',
      sourcemap: process.env.NODE_ENV !== 'production',
      loader: {
        '.js': 'jsx',
        '.jsx': 'jsx',
        '.ts': 'tsx',
        '.tsx': 'tsx',
        '.css': 'css',
        '.svg': 'dataurl',
        '.png': 'dataurl',
        '.jpg': 'dataurl',
        '.jpeg': 'dataurl',
        '.gif': 'dataurl',
      },
      define: {
        'process.env.NODE_ENV': '"production"',
      },
      target: ['es2020', 'chrome90', 'firefox90', 'safari14'],
      platform: 'browser',
      tsconfig: 'tsconfig.json',
      format: 'esm',
      metafile: true,
    });
    
    // Process HTML and assets
    await processHtml();
    await copyPublicAssets();
    await copyCssFiles();
    
    console.log('✅ Build completed successfully!');
  } catch (error) {
    console.error('❌ Build failed:', error.message);
    process.exit(1);
  }
}

// Run the build
runBuild();
