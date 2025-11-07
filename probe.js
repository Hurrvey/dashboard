const fs = require('fs');
const path = require('path');
const file = path.join('node_modules', 'chart.xkcd', 'dist', 'index.js');
const content = fs.readFileSync(file, 'utf-8');
const firstIndex = content.indexOf('function');
console.log(content.slice(firstIndex, firstIndex + 500));
