/**
 * Vendor frontend assets from akvo-rag-js into CKAN's public directory.
 */
const fs = require('fs');
const path = require('path');

const srcDir = path.resolve(__dirname, '../node_modules/akvo-rag-js/dist');
const destDir = path.resolve(__dirname, '../ckanext/akvorag/public');

if (!fs.existsSync(destDir)) {
  fs.mkdirSync(destDir, { recursive: true });
}

if (fs.existsSync(srcDir)) {
  const files = fs.readdirSync(srcDir);
  for (const file of files) {
    if (file !== 'index.html') {
      const srcFile = path.join(srcDir, file);
      const destFile = path.join(destDir, file);
      fs.copyFileSync(srcFile, destFile);
      console.log(`Copied ${file} -> ckanext/akvorag/public/${file}`);
    }
  }
  console.log('✅ Successfully vendored akvo-rag-js assets to ckanext/akvorag/public/');
} else {
  console.error(`❌ Source directory ${srcDir} does not exist. Run 'npm install' first.`);
  process.exit(1);
}
