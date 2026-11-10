// Node.js fallback generator for the concept plan. All coordinates are in feet.
const fs = require('fs');
const path = require('path');
const root = __dirname;
const panels = [
  ['GROUND FLOOR', '1 BEDROOM · PARKING · POOJA', [
    ['ELDER / GUEST BEDROOM',3,3,12,11,"12' x 11'"],['ATTACHED BATH',3,14,6,5,"6' x 5'"],['COMMON BATH',3,19,6,5,"6' x 5'"],['STAIR',3,24,9,10,'West / NW'],['UTILITY',13,3,5,8,"5' x 8'"],['KITCHEN',18,3,10,9,'SE · cook facing east'],['LIVING + DINING',12,12,11,12,'Open central space'],['DRAWING / FAMILY',12,24,11,10,"11' x 10'"],['ENTRY FOYER',23,17,5,7,'East entrance'],['POOJA',23,28,5,6,'NE · 5\' x 6\'']], true],
  ['FIRST FLOOR', '3 BEDROOMS · FAMILY LOUNGE · BALCONY', [
    ['MASTER BEDROOM',3,3,12,13,'SW · 12\' x 13\''],['DRESS + ENSUITE',3,16,8,7,"8' x 7'"],['BEDROOM 2',18,3,10,12,'SE · 10\' x 12\''],['COMMON BATH',13,3,5,7,"5' x 7'"],['FAMILY LOUNGE',11,12,12,11,"12' x 11'"],['BEDROOM 3',13,23,15,11,'North · 15\' x 11\''],['STAIR',3,24,9,10,'Continues from ground'],['EAST BALCONY',28.5,17,6.5,7,'Over entrance / porch']], false],
  ['SECOND FLOOR', 'MULTIPURPOSE ROOM · OPEN TERRACE', [
    ['MULTIPURPOSE / GYM',9,3,8,13,"8' x 13'"],['POWDER + STORE',3,16,7,6,"7' x 6'"],['STAIR HEADROOM',3,24,9,10,'West / NW'],['ROOF GARDEN + PERGOLA',17,3,11,31,'Open terrace · east / north'],['O.H. TANK',3,3,6,6,'SW raised platform']], false]
];
const offsets = [0,50,100], d=[];
const p=(c,v)=>d.push(String(c),String(v));
function line(x1,y1,x2,y2,layer='WALLS'){[[0,'LINE'],[8,layer],[10,x1],[20,y1],[30,0],[11,x2],[21,y2],[31,0]].forEach(([c,v])=>p(c,typeof v==='number'?v.toFixed(3):v));}
function rect(x,y,w,h,l){line(x,y,x+w,y,l);line(x+w,y,x+w,y+h,l);line(x+w,y+h,x,y+h,l);line(x,y+h,x,y,l);}
function label(s,x,y,size=.65,layer='TEXT'){const cadText=String(s).replaceAll('·','/').replaceAll('–','-').replaceAll('—','-').replace(/[^\x20-\x7E]/g,'');[[0,'TEXT'],[8,layer],[10,x],[20,y],[30,0],[40,size],[1,cadText],[72,1],[11,x],[21,y],[31,0],[73,2]].forEach(([c,v])=>p(c,typeof v==='number'?v.toFixed(3):v));}
p(0,'SECTION');p(2,'HEADER');p(9,'$ACADVER');p(1,'AC1015');p(9,'$INSUNITS');p(70,2);p(0,'ENDSEC');
p(0,'SECTION');p(2,'TABLES');p(0,'TABLE');p(2,'LAYER');p(70,9);
for(const [name,color] of [['WALLS',7],['ROOMS',8],['TEXT',3],['SITE',9],['PARKING',30],['POOJA',4],['BALCONY',40],['STAIRS',6],['DIM',2]]){p(0,'LAYER');p(2,name);p(70,0);p(62,color);p(6,'CONTINUOUS');}
p(0,'ENDTAB');p(0,'ENDSEC');p(0,'SECTION');p(2,'ENTITIES');
for(let i=0;i<panels.length;i++){const [title,sub,rooms,site]=panels[i],o=offsets[i];label(title,o+18.75,43.5,1.1);label(sub,o+18.75,41.8,.55);
 if(site){rect(o,0,37.5,37,'SITE');label("PLOT 37.5' x 37'",o+18.75,38,.7);rect(o+2.5,2.5,26,32,'WALLS');rect(o+28.5,3,8.5,17,'PARKING');label('CAR PORCH',o+32.75,12,.7,'PARKING');label("9' x 17'",o+32.75,10.5,.6,'PARKING');label('EAST ROAD',o+39,10,.7,'SITE');label('GATE',o+36,4,.55,'PARKING');} else rect(o+2.5,2.5,26,32,'WALLS');
 for(const [name,x,y,w,h,note] of rooms){let layer=name==='POOJA'?'POOJA':name.includes('STAIR')?'STAIRS':name.includes('BALCONY')||name.includes('GARDEN')?'BALCONY':'ROOMS';rect(o+x,y,w,h,layer);label(name,o+x+w/2,y+h/2+.35,.55,layer);label(note,o+x+w/2,y+h/2-.55,.42,layer);}
 line(o+34.2,31,o+34.2,35,'DIM');line(o+34.2,35,o+33.6,33.8,'DIM');line(o+34.2,35,o+34.8,33.8,'DIM');label('N',o+34.2,35.8,.7,'DIM');if(site){label("37.5'",o+18.75,-1.7,.65,'DIM');label("37'",o-1.2,18.5,.65,'DIM');}}
p(0,'ENDSEC');p(0,'EOF');fs.writeFileSync(path.join(root,'Chatgpt_plan.dxf'),d.join('\n'),'ascii');
// Draw a compact presentation SVG with north at the top.
let s=['<svg xmlns="http://www.w3.org/2000/svg" width="2220" height="1118" viewBox="0 0 123 62"><rect width="123" height="62" fill="#f7f4ed"/>','<style>text{font-family:Arial,sans-serif;fill:#243344}.title{font-size:1.4px;font-weight:bold;letter-spacing:.04em}.sub{font-size:.62px;fill:#617080}.room{font-size:.52px;font-weight:bold;text-anchor:middle}.note{font-size:.42px;fill:#526170;text-anchor:middle}.dim{font-size:.55px;fill:#526170;text-anchor:middle}</style>'];
function svgRect(x,y,w,h,fill,stroke='#324a5f',sw=.11){s.push(`<rect x="${x}" y="${53-y-h}" width="${w}" height="${h}" fill="${fill}" stroke="${stroke}" stroke-width="${sw}"/>`);}
function txt(t,x,y,cls,anchor='middle'){s.push(`<text class="${cls}" x="${x}" y="${53-y}" text-anchor="${anchor}">${String(t).replaceAll('&','&amp;').replaceAll('<','&lt;')}</text>`);}
for(let i=0;i<panels.length;i++){const [title,sub,rooms,site]=panels[i],o=3+i*40;txt(title,o+18.75,44.3,'title');txt(sub,o+18.75,42.8,'sub');if(site){svgRect(o,0,37.5,37,'#fffdf8','#87919a',.1);svgRect(o+2.5,2.5,26,32,'#f1eee6','#263e54',.2);svgRect(o+28.5,3,8.5,17,'#f6ebdc','#c98643',.13);txt('CAR PORCH',o+32.75,12.2,'room');txt("9' x 17'",o+32.75,10.8,'note');txt('EAST ROAD',o+39,11,'note','start');txt('37.5 ft',o+18.75,-1,'dim');txt('37 ft',o-1,18.5,'dim');}else svgRect(o+2.5,2.5,26,32,'#f1eee6','#263e54',.2);
for(const [name,x,y,w,h,note] of rooms){const fill=name==='POOJA'?'#e7f2ed':name.includes('STAIR')?'#eee8df':name.includes('BALCONY')||name.includes('GARDEN')?'#e8f0df':name==='O.H. TANK'?'#e8edf3':'#fffdf8';svgRect(o+x,y,w,h,fill,'#597184',.09);txt(name,o+x+w/2,y+h/2+.2,'room');txt(note,o+x+w/2,y+h/2-.7,'note');}s.push(`<path d="M ${o+34.2} 22 L ${o+34.2} 18 M ${o+34.2} 18 l -.55 1.2 m .55 -1.2 l .55 1.2" stroke="#526170" fill="none" stroke-width=".12"/>`);txt('N',o+34.2,16.7,'dim');}
s.push('<text x="3" y="60" style="font:.52px Arial;fill:#617080">CONCEPT PLAN · DIMENSIONS IN FEET · VERIFY LOCAL SETBACKS, STRUCTURE AND SERVICES BEFORE CONSTRUCTION</text></svg>');fs.writeFileSync(path.join(root,'Chatgpt_plan.svg'),s.join('\n'),'utf8');
console.log('Created Chatgpt_plan.dxf and Chatgpt_plan.svg');
