const fs = require('fs');
const content = fs.readFileSync('node_modules/chart.xkcd/dist/chart.xkcd.min.js', 'utf8');
const idx = content.indexOf('"legend"');
console.log(idx);
