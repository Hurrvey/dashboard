const fs = require('fs');
const content = fs.readFileSync('node_modules/chart.xkcd/dist/index.js', 'utf8');
const idx = content.indexOf('attr("width",8)');
console.log('idx', idx);
console.log(content.slice(idx - 150, idx + 150));
