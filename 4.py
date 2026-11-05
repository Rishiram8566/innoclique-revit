"""
Innoclique - landing page generator + local server.
Pure Python standard library: no pip installs, no hosting cost.

Run:   python innoclique_site.py
Open:  http://localhost:8000
Also writes a static index.html you can upload to any free host
(GitHub Pages, Netlify, Cloudflare Pages).

v2: LOD option in "Plan to 3D", and a 3D view (with mismatches) in "CAD vs Revit".
"""
import http.server
import socketserver
import webbrowser
from html import escape
from pathlib import Path

PORT = 8000

# Innoclique logo. To keep your original webp logo, replace the whole LOGO = ... line
# below with your original LOGO = "data:image/webp;base64,..." line.
LOGO = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 163 36'%3E"
        "%3Ccircle cx='18' cy='18' r='10' fill='%23f09c00'/%3E%3Ccircle cx='18' cy='18' r='15' fill='none' "
        "stroke='%230c6cf0' stroke-width='3'/%3E%3Ctext x='40' y='25' font-family='Arial' font-weight='700' "
        "font-size='20' fill='%231f2a37'%3EInnoclique%3C/text%3E%3C/svg%3E")
_logo_file = Path(__file__).with_name("logo.txt")  # optional: put the data URI in logo.txt
if _logo_file.exists():
    LOGO = _logo_file.read_text(encoding="utf-8").strip()

# ----------------------------- CONTENT ------------------------------------
SITE = {
    "name": "Innoclique",
    "tagline": "Turn flat plans into 3D models in seconds.",
    "intro": (
        "Upload a CAD drawing and your Revit export. Innoclique aligns them, checks every "
        "measurement against your level of development (LOD), and highlights each mismatch."
    ),
    "domain": "innoclique.com",
}

PRODUCTS = [
    {
        "name": "Tesseract",
        "kind": "Scan to BIM",
        "desc": "A laser scan of a building or structure, returned as an IFC or "
                "Revit model you can check against the scan. Shell, Shell + MEP, "
                "or Civil + outdoor.",
        "formats": "E57, LAS, LAZ in \u00b7 IFC, Revit out",
        "link": "#contact",
    },
]

DELIVERABLES = [
    ("Floor plans and areas by room", ["PDF sheet", "DXF drawing"],
     "Architects, facilities, brokers"),
    ("Equipment, fixture and asset counts",
     ["CSV schedule", "each item pinned in the viewer"],
     "Facilities, MEP, owners"),
    ("Quantity takeoffs and stockpile inventories",
     ["CSV with lengths, areas and volumes"],
     "Estimators, contractors, yards"),
    ("Site survey of a drone capture",
     ["PDF survey pack", "GeoJSON layers", "CSV table"],
     "Surveyors, civil, planners"),
    ("BIM model (Shell, Shell + MEP, Civil + outdoor)",
     ["IFC or Revit", "element schedules as CSV"],
     "Scanning firms, BIM managers"),
    ("Answers to anything else",
     ["Typed into the viewer, answered on the same page"],
     "Everyone"),
]

# ----------------------------- STYLES -------------------------------------
CSS = """
:root{color-scheme:light;--bg:#ffffff;--surface:#ffffff;--text:#1f2a37;--muted:#64748b;--accent:#0c6cf0;--accent2:#f09c00;--line:#e2e8f0;--radius:12px;--shadow:0 4px 24px rgba(15,23,42,.06)}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{font-family:Inter,"Segoe UI",system-ui,-apple-system,sans-serif;-webkit-font-smoothing:antialiased;
background:var(--bg);color:var(--text);line-height:1.6}
a{color:inherit;text-decoration:none}
.wrap{max-width:1080px;margin:0 auto;padding:0 24px}
header{position:sticky;top:0;z-index:10;backdrop-filter:blur(10px);
background:color-mix(in srgb,var(--bg) 80%,transparent);
border-bottom:1px solid var(--line)}
nav{display:flex;align-items:center;justify-content:space-between;height:64px}
.logo img{height:36px;width:auto;display:block}
nav .links{display:flex;gap:24px;align-items:center;font-size:.95rem;color:var(--muted)}
nav .links a:hover{color:var(--text)}
.btn{display:inline-block;padding:10px 20px;border-radius:999px;
background:var(--accent);color:#fff!important;font-weight:600;font-size:.95rem;transition:background .16s,transform .16s}
.btn:hover{background:#0a5cd0}
.btn.alt{background:var(--accent2)}.btn.alt:hover{background:#d98a00}
.btn.ghost{background:transparent;border:1px solid var(--line);color:var(--text)!important}
.hero{padding:110px 0 90px;text-align:center;position:relative;overflow:hidden;background:linear-gradient(180deg,#eef5ff 0%,#ffffff 100%)}
.hero canvas{position:absolute;inset:0;width:100%;height:100%;opacity:.4;z-index:0}
.hero .wrap{position:relative;z-index:1}
h1{font-size:clamp(2.2rem,6vw,4rem);line-height:1.1;margin-bottom:20px}
h1 em{font-style:normal;color:var(--accent)}
.hero p{max-width:640px;margin:0 auto 32px;color:var(--muted);font-size:1.1rem}
.hero .cta{display:flex;gap:12px;justify-content:center;flex-wrap:wrap}
.flow{margin-top:36px;color:var(--muted);letter-spacing:2px;font-size:.85rem;
text-transform:uppercase}
section{padding:80px 0;border-top:1px solid var(--line)}
.eyebrow{color:var(--accent2);font-size:.8rem;font-weight:700;
letter-spacing:2px;text-transform:uppercase;margin-bottom:8px}
h2{font-size:clamp(1.6rem,3.5vw,2.3rem);margin-bottom:12px}
.sub{color:var(--muted);max-width:620px;margin-bottom:36px}
.grid{display:grid;gap:20px;grid-template-columns:repeat(auto-fit,minmax(240px,1fr))}
.card{background:var(--surface);border:1px solid var(--line);
border-radius:var(--radius);padding:26px;box-shadow:var(--shadow);transition:transform .2s,border-color .2s}
.card:hover{transform:translateY(-3px);border-color:var(--accent)}
.card h3{margin-bottom:4px}
.tag{color:var(--accent);font-size:.85rem;margin-bottom:10px}
.muted{color:var(--muted);font-size:.92rem}
.tbl-wrap{overflow-x:auto;border:1px solid var(--line);border-radius:var(--radius);
background:var(--surface)}
table{width:100%;border-collapse:collapse;min-width:640px;font-size:.95rem}
th,td{text-align:left;padding:14px 18px;border-bottom:1px solid var(--line);vertical-align:top}
th{color:var(--muted);font-size:.78rem;letter-spacing:1.5px;text-transform:uppercase}
tr:last-child td{border-bottom:0}
code{background:color-mix(in srgb,var(--accent) 14%,transparent);color:var(--accent);
padding:2px 8px;border-radius:6px;font-size:.85rem;margin-right:4px;display:inline-block}
.two{display:grid;gap:20px;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));margin-top:28px}
.two .card p{margin-top:8px}
.contact{text-align:center}
.contact .sub{margin:0 auto 28px}
form{max-width:520px;margin:28px auto 0;display:grid;gap:12px;text-align:left}
input,textarea,select{width:100%;padding:12px 14px;border-radius:10px;
border:1px solid var(--line);background:var(--surface);color:var(--text);font:inherit}
input:focus,textarea:focus,select:focus{outline:2px solid var(--accent)}
button{border:0;cursor:pointer;font:inherit}
footer{background:#f8fafc;border-top:1px solid var(--line);padding:50px 0 30px;color:var(--muted);font-size:.92rem}
.fgrid{display:grid;gap:30px;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));margin-bottom:30px}
footer h4{color:var(--text);margin-bottom:10px;font-size:.95rem}
footer a{display:block;padding:3px 0}
footer a:hover{color:var(--text)}
@media(max-width:640px){nav .links a:not(.btn){display:none}.hero{padding:70px 0 60px}}
"""

# ----------------------------- SCRIPT -------------------------------------
# Lightweight animated point-cloud background (canvas, no libraries).
JS = """
(function(){
  const c=document.getElementById('cloud'),x=c.getContext('2d');
  let w,h,pts=[];
  function size(){w=c.width=c.offsetWidth;h=c.height=c.offsetHeight;
    pts=Array.from({length:Math.min(140,Math.floor(w/8))},()=>({
      x:Math.random()*w,y:Math.random()*h,z:Math.random()*.8+.2,
      vx:(Math.random()-.5)*.25,vy:(Math.random()-.5)*.25}));}
  function draw(){
    x.clearRect(0,0,w,h);
    const col=getComputedStyle(document.documentElement).getPropertyValue('--accent').trim();
    x.fillStyle=col;x.strokeStyle=col;
    for(const p of pts){
      p.x+=p.vx;p.y+=p.vy;
      if(p.x<0||p.x>w)p.vx*=-1;if(p.y<0||p.y>h)p.vy*=-1;
      x.globalAlpha=p.z*.8;x.beginPath();x.arc(p.x,p.y,p.z*2,0,6.283);x.fill();}
    for(let i=0;i<pts.length;i++)for(let j=i+1;j<pts.length;j++){
      const dx=pts[i].x-pts[j].x,dy=pts[i].y-pts[j].y,d=dx*dx+dy*dy;
      if(d<7000){x.globalAlpha=(1-d/7000)*.25;x.beginPath();
        x.moveTo(pts[i].x,pts[i].y);x.lineTo(pts[j].x,pts[j].y);x.stroke();}}
    requestAnimationFrame(draw);}
  size();addEventListener('resize',size);
  if(!matchMedia('(prefers-reduced-motion:reduce)').matches)draw();
})();

// Contact form: opens the visitor's email client (no backend needed).
function sendScan(e){
  e.preventDefault();
  const f=e.target,to='contact@%(domain)s';
  const subject=encodeURIComponent(f.topic.value+' - '+f.name.value);
  const body=encodeURIComponent(f.msg.value+'\\n\\nFrom: '+f.name.value+' <'+f.email.value+'>\\n(Attach your scan file or paste a link.)');
  location.href='mailto:'+to+'?subject='+subject+'&body='+body;
}
""" % {"domain": SITE["domain"]}


# ----------------------- PLAN -> 3D TOOL (runs in browser) -----------------
TOOL_CSS = """
.tool{display:grid;gap:20px;grid-template-columns:320px 1fr;align-items:start}
@media(max-width:860px){.tool{grid-template-columns:1fr}}
.panel{box-shadow:var(--shadow);background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);
padding:18px;display:grid;gap:12px}
.drop{display:grid;gap:4px;place-items:center;text-align:center;padding:26px 12px;
border:2px dashed var(--line);border-radius:12px;cursor:pointer}
.drop:hover,.drop.on{border-color:var(--accent)}
.ctl label{display:flex;justify-content:space-between;font-size:.85rem;color:var(--muted)}
.ctl input{padding:0}
.chk{display:flex;gap:8px;align-items:center;font-size:.9rem}
.chk input{width:auto}
.v3d{height:560px;border:1px solid var(--line);border-radius:var(--radius);
background:var(--surface);overflow:hidden}
.v3d canvas{display:block}
.stats{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));margin:16px 0}
.stats .card{padding:14px}.stats h3{font-size:1.25rem}
.btns{display:flex;flex-wrap:wrap;gap:8px}
.btns button{padding:8px 14px;font-size:.85rem}
tr.rr{cursor:pointer}tr.rr:hover td{background:color-mix(in srgb,var(--accent) 10%,transparent)}
"""


def ctl(i, label, lo, hi, step, val):
    return (f'<div class="ctl"><label>{label}<span id="o_{i}">{val}</span></label>'
            f'<input type="range" id="{i}" min="{lo}" max="{hi}" step="{step}" value="{val}"></div>')


def chk(i, label, on=True):
    return (f'<label class="chk"><input type="checkbox" id="{i}"'
            f'{" checked" if on else ""}> {label}</label>')


LOD_OPTIONS = (
    '<option value="100">LOD 100 - Massing</option>'
    '<option value="200">LOD 200 - Approximate</option>'
    '<option value="300" selected>LOD 300 - Precise</option>'
    '<option value="350">LOD 350 - Coordinated</option>'
    '<option value="400">LOD 400 - Fabrication</option>'
    '<option value="500">LOD 500 - As-built</option>')

TOOL_HTML = f"""
<section id="convert"><div class="wrap">
  <div class="eyebrow">Try it</div>
  <h2>Upload a 2D plan. Get a 3D model.</h2>
  <p class="sub">Drop in a floor plan (PNG, JPG or PDF). It is converted inside your
  browser, so nothing is uploaded to a server and it costs nothing to run.</p>
  <div class="tool">
    <aside class="panel">
      <label class="drop" id="drop"><input type="file" id="file" accept="image/*,.pdf" hidden>
        <b>Drop a plan here</b><span class="muted">or click to choose (PNG, JPG, PDF)</span></label>
      <button class="btn ghost" id="sample" type="button">Try a sample plan</button>
      <div id="status" class="muted">Waiting for a plan...</div>
      {ctl("rw", "Real width of plan (m)", 3, 100, 0.5, 12)}
      <div class="ctl"><label>Level of development (LOD)</label><select id="lod">{LOD_OPTIONS}</select></div>
      <div id="lodnote" class="muted"></div>
      {ctl("wh", "Wall height (m)", 2, 6, 0.1, 2.7)}
      {ctl("thr", "Line threshold", 1, 254, 1, 128)}
      {ctl("thick", "Thicken thin lines", 0, 3, 1, 0)}
      {ctl("speck", "Remove specks / text (px)", 0, 60, 1, 6)}
      {ctl("gap", "Close doorways (px)", 0, 25, 1, 9)}
      {chk("inv", "Light lines on dark background", False)}
      {chk("tsolid", "Solid walls")}{chk("tpts", "Point cloud", False)}
      {chk("tfloor", "Floor and rooms")}{chk("tpins", "Room labels")}
      <div class="btns">
        <button class="btn ghost" id="mbtn" type="button">Measure</button>
        <button class="btn ghost" id="mclr" type="button">Clear</button>
      </div>
      <div id="mres" class="muted">Measure: click two points on the floor.</div>
      <div class="btns">
        <button class="btn" id="obj" type="button">.OBJ</button>
        <button class="btn" id="xyz" type="button">.XYZ points</button>
        <button class="btn" id="csv" type="button">Rooms .CSV</button>
        <button class="btn" id="png" type="button">Screenshot</button>
      </div>
    </aside>
    <div>
      <div id="v3d" class="v3d"></div>
      <div class="stats" id="stats"></div>
      <div class="tbl-wrap"><table>
        <thead><tr><th>Room</th><th>Area</th><th>Size (w x d)</th></tr></thead>
        <tbody id="rooms"><tr><td colspan="3" class="muted">Rooms appear here. Click one to fly to it.</td></tr></tbody>
      </table></div>
    </div>
  </div>
</div></section>
"""

TOOL_JS = r"""
(function(){
const $=id=>document.getElementById(id);
const S={src:null,fresh:false,reth:false,fit:false,rects:[],rooms:[],pts:null,wall:null,floor:null,pins:[],c:.03,ox:0,oz:0,size:10};
let renderer,scene,camera,controls,dyn=[],measuring=false,mpts=[],mobj=[],down=[0,0];
const view=$('v3d');
window.IQ={otsu,dilate,ccl,rectsOf,tag};
function status(t,e){const s=$('status');s.textContent=t;s.style.color=e?'#e5484d':'';}
if(!window.THREE){status('3D library failed to load. Check your internet connection.',true);return;}
const hgt=()=>parseFloat($('wh').value);
/* LOD: resolution used to read the plan + what is built */
const LODRES={100:200,200:320,300:480,350:640,400:900,500:1200};
const LN={100:'Massing only: one solid block of the footprint, no rooms.',200:'Approximate walls, small details removed, rooms.',
  300:'Precise walls, floor and rooms.',350:'Finer reading of the plan for coordination.',400:'High detail for fabrication.',500:'Highest detail, as-built.'};

/* ---------- 3D scene ---------- */
function init3d(){
  scene=new THREE.Scene();
  camera=new THREE.PerspectiveCamera(50,1,.1,2000);camera.position.set(0,10,12);
  renderer=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true,alpha:true});
  view.appendChild(renderer.domElement);
  controls=new THREE.OrbitControls(camera,renderer.domElement);controls.enableDamping=true;
  scene.add(new THREE.HemisphereLight(0xffffff,0x445566,.95));
  const d=new THREE.DirectionalLight(0xffffff,.8);d.position.set(5,10,6);scene.add(d);
  resize();addEventListener('resize',resize);
  (function loop(){requestAnimationFrame(loop);controls.update();renderer.render(scene,camera);})();
  const rc=new THREE.Raycaster(),pl=new THREE.Plane(new THREE.Vector3(0,1,0),0),el=renderer.domElement;
  el.addEventListener('pointerdown',e=>{down=[e.clientX,e.clientY];});
  el.addEventListener('pointerup',e=>{
    if(!measuring||Math.hypot(e.clientX-down[0],e.clientY-down[1])>5)return;
    const r=el.getBoundingClientRect();
    rc.setFromCamera({x:(e.clientX-r.left)/r.width*2-1,y:-((e.clientY-r.top)/r.height)*2+1},camera);
    const p=new THREE.Vector3();if(!rc.ray.intersectPlane(pl,p))return;
    mpts.push(p);
    const dot=new THREE.Mesh(new THREE.SphereGeometry(S.size*.008,12,12),new THREE.MeshBasicMaterial({color:0xff5555,depthTest:false}));
    dot.position.copy(p);dot.renderOrder=10;scene.add(dot);mobj.push(dot);
    if(mpts.length===2){
      const ln=new THREE.Line(new THREE.BufferGeometry().setFromPoints(mpts),new THREE.LineBasicMaterial({color:0xff5555,depthTest:false}));
      ln.renderOrder=10;scene.add(ln);mobj.push(ln);
      $('mres').textContent='Distance: '+mpts[0].distanceTo(mpts[1]).toFixed(2)+' m';mpts=[];
    }
  });
}
function resize(){const w=view.clientWidth,h=view.clientHeight;renderer.setSize(w,h);camera.aspect=w/h;camera.updateProjectionMatrix();}

/* ---------- image helpers ---------- */
function otsu(h,n){let sum=0;for(let i=0;i<256;i++)sum+=i*h[i];let sB=0,wB=0,mx=0,t=128;
  for(let i=0;i<256;i++){wB+=h[i];if(!wB)continue;const wF=n-wB;if(!wF)break;sB+=i*h[i];
    const mB=sB/wB,mF=(sum-sB)/wF,b=wB*wF*(mB-mF)*(mB-mF);if(b>mx){mx=b;t=i;}}return t;}
function dilate(m,W,H,r){if(r<1)return m;const t=new Uint8Array(m.length),o=new Uint8Array(m.length);
  for(let y=0;y<H;y++)for(let x=0;x<W;x++){let v=0;for(let k=-r;k<=r&&!v;k++){const q=x+k;if(q>=0&&q<W&&m[y*W+q])v=1;}t[y*W+x]=v;}
  for(let y=0;y<H;y++)for(let x=0;x<W;x++){let v=0;for(let k=-r;k<=r&&!v;k++){const q=y+k;if(q>=0&&q<H&&t[q*W+x])v=1;}o[y*W+x]=v;}
  return o;}
function ccl(m,W,H,val){const lab=new Int32Array(W*H),sizes=[0],st=[];let n=0;
  for(let s=0;s<W*H;s++){if(lab[s]||m[s]!==val)continue;n++;let c=0;st.push(s);lab[s]=n;
    while(st.length){const p=st.pop();c++;const x=p%W,y=(p/W)|0;
      if(x>0&&!lab[p-1]&&m[p-1]===val){lab[p-1]=n;st.push(p-1);}
      if(x<W-1&&!lab[p+1]&&m[p+1]===val){lab[p+1]=n;st.push(p+1);}
      if(y>0&&!lab[p-W]&&m[p-W]===val){lab[p-W]=n;st.push(p-W);}
      if(y<H-1&&!lab[p+W]&&m[p+W]===val){lab[p+W]=n;st.push(p+W);}}
    sizes[n]=c;}
  return{lab,sizes};}
function rectsOf(m,W,H){const out=[];let act=new Map();
  for(let y=0;y<H;y++){const cur=new Map();let x=0;
    while(x<W){if(m[y*W+x]){const x0=x;while(x<W&&m[y*W+x])x++;const k=x0+'_'+(x-x0),a=act.get(k);
      if(a){a.h++;cur.set(k,a);}else{const r={x:x0,y:y,w:x-x0,h:1};cur.set(k,r);out.push(r);}}else x++;}
    act=cur;}
  return out;}
function hsl(h,s,l){const a=s*Math.min(l,1-l),f=n=>{const k=(n+h/30)%12;return l-a*Math.max(-1,Math.min(k-3,9-k,1));};return[f(0)*255,f(8)*255,f(4)*255];}
function tag(t){const k=document.createElement('canvas');k.width=300;k.height=80;const x=k.getContext('2d');
  x.fillStyle='rgba(255,255,255,.95)';x.fillRect(0,0,300,80);x.strokeStyle='#f09c00';x.lineWidth=4;x.strokeRect(2,2,296,76);
  x.fillStyle='#1f2a37';x.font='bold 30px sans-serif';x.textAlign='center';x.textBaseline='middle';x.fillText(t,150,42);
  const s=new THREE.Sprite(new THREE.SpriteMaterial({map:new THREE.CanvasTexture(k),depthTest:false,transparent:true}));s.renderOrder=9;return s;}

/* ---------- main pipeline: plan image -> walls, rooms, 3D ---------- */
function analyze(){
  const cv=S.src;if(!cv)return;
  const w=cv.width,h=cv.height,d=cv.getContext('2d').getImageData(0,0,w,h).data,first=S.fresh;
  if(first){let s=0,n=0;for(let i=0;i<d.length;i+=28){s+=d[i];n++;}$('inv').checked=s/n<110;}
  const inv=$('inv').checked,f=Math.max(1,Math.ceil(Math.max(w,h)/LODRES[+$('lod').value])),W=Math.ceil(w/f),H=Math.ceil(h/f);
  const g=new Uint8Array(W*H).fill(255);
  for(let y=0;y<h;y++){const row=((y/f)|0)*W;for(let x=0;x<w;x++){const i=(y*w+x)*4;
    let v=(d[i]*.3+d[i+1]*.59+d[i+2]*.11)|0;if(inv)v=255-v;const k=row+((x/f)|0);if(v<g[k])g[k]=v;}}
  if(first||S.reth){const hs=new Array(256).fill(0);for(let i=0;i<g.length;i++)hs[g[i]]++;
    const t=Math.min(250,otsu(hs,W*H)+1);$('thr').value=t;$('o_thr').textContent=t;}
  S.fresh=S.reth=false;
  const thr=+$('thr').value;let m=new Uint8Array(W*H);
  for(let i=0;i<m.length;i++)m[i]=g[i]<thr?1:0;
  m=dilate(m,W,H,+$('thick').value);
  const lodv=+$('lod').value,sp=Math.max(+$('speck').value,lodv<=200?12:0);
  if(sp>0){const L=ccl(m,W,H,1);for(let i=0;i<m.length;i++)if(m[i]&&L.sizes[L.lab[i]]<sp)m[i]=0;}
  dyn.forEach(o=>{scene.remove(o);if(o.geometry)o.geometry.dispose();});dyn=[];S.pins=[];
  let rects=rectsOf(m,W,H);
  if(!rects.length){S.rects=[];S.rooms=[];status('No walls found. Try raising the line threshold.',true);return;}
  const c=(+$('rw').value)/W,gap=+$('gap').value,ox=-W*c/2,oz=-H*c/2;
  Object.assign(S,{c,ox,oz,size:Math.max(W,H)*c,rects});
  /* rooms: close doorways, flood-fill, drop the outside */
  const L=ccl(dilate(m,W,H,gap),W,H,0),lab=L.lab,ext=new Set();
  for(let x=0;x<W;x++){ext.add(lab[x]);ext.add(lab[(H-1)*W+x]);}
  for(let y=0;y<H;y++){ext.add(lab[y*W]);ext.add(lab[y*W+W-1]);}
  for(let it=0;it<gap;it++){const nl=lab.slice();
    for(let y=0;y<H;y++)for(let x=0;x<W;x++){const p=y*W+x;if(lab[p]||m[p])continue;
      const v=(x>0&&lab[p-1])||(x<W-1&&lab[p+1])||(y>0&&lab[p-W])||(y<H-1&&lab[p+W]);if(v)nl[p]=v;}
    lab.set(nl);}
  const R={};
  for(let p=0;p<W*H;p++){const id=lab[p];if(!id||ext.has(id))continue;const x=p%W,y=(p/W)|0;
    const r=R[id]||(R[id]={id,n:0,sx:0,sy:0,x0:W,x1:0,y0:H,y1:0});
    r.n++;r.sx+=x;r.sy+=y;r.x0=Math.min(r.x0,x);r.x1=Math.max(r.x1,x);r.y0=Math.min(r.y0,y);r.y1=Math.max(r.y1,y);}
  const minPx=Math.max(20,.8/(c*c));
  const rooms=Object.values(R).filter(r=>r.n>=minPx).sort((a,b)=>a.y0-b.y0||a.x0-b.x0);
  rooms.forEach(r=>{r.area=r.n*c*c;r.w=(r.x1-r.x0+1)*c;r.d=(r.y1-r.y0+1)*c;
    r.cx=ox+(r.sx/r.n+.5)*c;r.cz=oz+(r.sy/r.n+.5)*c;});
  /* LOD 100 = massing: fill the whole footprint into one solid block, no rooms */
  if(lodv===100){const fm=new Uint8Array(W*H);for(let p=0;p<W*H;p++)fm[p]=(m[p]||(lab[p]&&!ext.has(lab[p])))?1:0;
    rects=rectsOf(fm,W,H);rooms.length=0;}
  S.rects=rects;S.rooms=rooms;
  /* floor texture, tinted by room */
  const fc=document.createElement('canvas');fc.width=W;fc.height=H;
  const fx=fc.getContext('2d'),im=fx.createImageData(W,H),px=im.data,col={};
  rooms.forEach((r,i)=>col[r.id]=hsl((i*47+25)%360,.6,.8));
  for(let p=0;p<W*H;p++){const cc=m[p]?[70,80,95]:col[lab[p]];if(cc){const q=p*4;px[q]=cc[0];px[q+1]=cc[1];px[q+2]=cc[2];px[q+3]=255;}}
  fx.putImageData(im,0,0);
  const tex=new THREE.CanvasTexture(fc);tex.magFilter=THREE.NearestFilter;
  const floor=new THREE.Mesh(new THREE.PlaneGeometry(W*c,H*c),new THREE.MeshBasicMaterial({map:tex,transparent:true}));
  floor.rotation.x=-Math.PI/2;floor.position.y=.002;
  /* walls: merged boxes, one InstancedMesh */
  const wall=new THREE.InstancedMesh(new THREE.BoxGeometry(1,1,1),new THREE.MeshStandardMaterial({color:0x94a3b8,roughness:.8}),rects.length);
  const m4=new THREE.Matrix4(),q0=new THREE.Quaternion();
  rects.forEach((r,i)=>{m4.compose(new THREE.Vector3(ox+(r.x+r.w/2)*c,.5,oz+(r.y+r.h/2)*c),q0,new THREE.Vector3(r.w*c,1,r.h*c));wall.setMatrixAt(i,m4);});
  /* point cloud sampled on wall surfaces (unit height, scaled with the walls) */
  let tot=0;const faces=rects.map(r=>{const bw=r.w*c,bd=r.h*c,A=[bw*bd,bw*2.7,bw*2.7,bd*2.7,bd*2.7],T=A.reduce((a,b)=>a+b);tot+=T;return{r,bw,bd,A,T};});
  const dens=40000/tot,pos=[];
  faces.forEach(o=>{const n=Math.max(3,Math.round(o.T*dens)),x0=ox+o.r.x*c,z0=oz+o.r.y*c;
    for(let i=0;i<n;i++){let p=Math.random()*o.T,k=0;while(k<4&&p>o.A[k]){p-=o.A[k];k++;}
      const u=Math.random(),v=Math.random();
      if(k===0)pos.push(x0+u*o.bw,1,z0+v*o.bd);else if(k===1)pos.push(x0+u*o.bw,v,z0);
      else if(k===2)pos.push(x0+u*o.bw,v,z0+o.bd);else if(k===3)pos.push(x0,v,z0+u*o.bd);
      else pos.push(x0+o.bw,v,z0+u*o.bd);}});
  const pg=new THREE.BufferGeometry();pg.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));
  const pts=new THREE.Points(pg,new THREE.PointsMaterial({color:0x0c6cf0,size:S.size*.004}));
  scene.add(floor,wall,pts);dyn.push(floor,wall,pts);Object.assign(S,{floor,wall,pts});
  rooms.forEach((r,i)=>{const t=tag('R'+(i+1)+' | '+r.area.toFixed(1)+' m2');t.scale.set(S.size*.2,S.size*.2*80/300,1);
    t.position.set(r.cx,.5,r.cz);scene.add(t);dyn.push(t);S.pins.push(t);});
  vis();hh();
  if(S.fit){camera.position.set(0,S.size*.9,S.size*.8);controls.target.set(0,0,0);S.fit=false;}
  /* stats */
  let wa=0,x0=W,x1=0,y0=H,y1=0;
  rects.forEach(r=>{wa+=r.w*r.h;x0=Math.min(x0,r.x);x1=Math.max(x1,r.x+r.w);y0=Math.min(y0,r.y);y1=Math.max(y1,r.y+r.h);});
  const th=rects.map(r=>Math.min(r.w,r.h)).sort((a,b)=>a-b)[rects.length>>1]||1;
  const st=[['LOD',lodv],['Rooms',rooms.length],['Room area',rooms.reduce((a,r)=>a+r.area,0).toFixed(1)+' m2'],
    ['Footprint',((x1-x0)*c).toFixed(1)+' x '+((y1-y0)*c).toFixed(1)+' m'],
    ['Wall length (approx)',(wa/th*c).toFixed(1)+' m'],['Wall area (plan)',(wa*c*c).toFixed(1)+' m2'],
    ['Wall volume',(wa*c*c*hgt()).toFixed(1)+' m3'],['Wall blocks',rects.length]];
  $('stats').innerHTML=st.map(a=>'<div class="card"><div class="muted">'+a[0]+'</div><h3>'+a[1]+'</h3></div>').join('');
  $('rooms').innerHTML=rooms.length?rooms.map((r,i)=>'<tr class="rr" data-i="'+i+'"><td>Room '+(i+1)+'</td><td>'+r.area.toFixed(1)+' m2</td><td>'+r.w.toFixed(1)+' x '+r.d.toFixed(1)+' m</td></tr>').join(''):
    '<tr><td colspan="3" class="muted">'+(lodv===100?'LOD 100 is a massing model, rooms are not extracted.':'No closed rooms found. Increase "Close doorways".')+'</td></tr>';
  status('Done (LOD '+lodv+'): '+rooms.length+' rooms, '+rects.length+' wall blocks. Drag to orbit, scroll to zoom.');
}
function vis(){if(S.wall)S.wall.visible=$('tsolid').checked;if(S.pts)S.pts.visible=$('tpts').checked;
  if(S.floor)S.floor.visible=$('tfloor').checked;S.pins.forEach(p=>p.visible=$('tpins').checked);}
function hh(){const h=hgt();if(S.wall)S.wall.scale.y=h;if(S.pts)S.pts.scale.y=h;}

/* ---------- loading files ---------- */
async function loadFile(f){
  if(!f)return;status('Reading '+f.name+' ...');
  try{
    let cv;
    if(f.type==='application/pdf'||/\.pdf$/i.test(f.name)){
      if(!window.pdfjsLib)throw new Error('PDF reader not loaded (check internet).');
      pdfjsLib.GlobalWorkerOptions.workerSrc='https://cdn.jsdelivr.net/npm/pdfjs-dist@3.11.174/build/pdf.worker.min.js';
      const pdf=await pdfjsLib.getDocument({data:await f.arrayBuffer()}).promise,pg=await pdf.getPage(1),v0=pg.getViewport({scale:1}),
        vp=pg.getViewport({scale:1500/Math.max(v0.width,v0.height)});
      cv=document.createElement('canvas');cv.width=vp.width;cv.height=vp.height;
      const cx=cv.getContext('2d');cx.fillStyle='#fff';cx.fillRect(0,0,cv.width,cv.height);
      await pg.render({canvasContext:cx,viewport:vp}).promise;
    }else{
      const img=await new Promise((res,rej)=>{const i=new Image();i.onload=()=>res(i);i.onerror=()=>rej(new Error('Not a readable image'));i.src=URL.createObjectURL(f);});
      const sc=Math.min(1,1500/Math.max(img.width,img.height));
      cv=document.createElement('canvas');cv.width=Math.round(img.width*sc);cv.height=Math.round(img.height*sc);
      const cx=cv.getContext('2d');cx.fillStyle='#fff';cx.fillRect(0,0,cv.width,cv.height);cx.drawImage(img,0,0,cv.width,cv.height);
    }
    S.src=cv;S.fresh=true;S.fit=true;analyze();
  }catch(e){status('Error: '+e.message,true);}
}
function sample(){
  const cv=document.createElement('canvas');cv.width=900;cv.height=620;const x=cv.getContext('2d');
  x.fillStyle='#fff';x.fillRect(0,0,900,620);x.strokeStyle='#000';x.lineWidth=14;x.lineCap='butt';
  const L=(a,b,c,d)=>{x.beginPath();x.moveTo(a,b);x.lineTo(c,d);x.stroke();};
  x.strokeRect(40,40,820,540);
  L(420,40,420,235);L(420,265,420,580);L(40,300,135,300);L(165,300,420,300);
  L(420,360,575,360);L(605,360,860,360);L(640,360,640,455);L(640,485,640,580);
  S.src=cv;S.fresh=true;S.fit=true;analyze();
}

/* ---------- exports ---------- */
function dl(name,data,type){const a=document.createElement('a');
  a.href=String(data).startsWith('data:')?data:URL.createObjectURL(new Blob([data],{type:type||'text/plain'}));a.download=name;a.click();}
const ready=()=>S.rects.length?true:(status('Upload a plan first.',true),false);
function objText(){const v=[],f=[],H=hgt();let n=0;
  S.rects.forEach(r=>{const x0=S.ox+r.x*S.c,x1=x0+r.w*S.c,z0=S.oz+r.y*S.c,z1=z0+r.h*S.c;
    [[x0,0,z0],[x1,0,z0],[x1,0,z1],[x0,0,z1],[x0,H,z0],[x1,H,z0],[x1,H,z1],[x0,H,z1]].forEach(p=>v.push('v '+p.join(' ')));
    [[1,2,3,4],[5,8,7,6],[1,5,6,2],[2,6,7,3],[3,7,8,4],[4,8,5,1]].forEach(q=>f.push('f '+q.map(i=>i+n).join(' ')));n+=8;});
  return '# Innoclique plan to 3D (LOD '+$('lod').value+')\n'+v.join('\n')+'\n'+f.join('\n')+'\n';}

/* ---------- wire up UI ---------- */
init3d();
const drop=$('drop');
$('file').onchange=e=>loadFile(e.target.files[0]);
drop.ondragover=e=>{e.preventDefault();drop.classList.add('on');};
drop.ondragleave=()=>drop.classList.remove('on');
drop.ondrop=e=>{e.preventDefault();drop.classList.remove('on');loadFile(e.dataTransfer.files[0]);};
$('sample').onclick=sample;
let tm;
document.querySelectorAll('.panel input[type=range]').forEach(el=>el.addEventListener('input',()=>{
  $('o_'+el.id).textContent=el.value;if(el.id==='wh'){hh();return;}clearTimeout(tm);tm=setTimeout(analyze,120);}));
$('inv').onchange=()=>{S.reth=true;analyze();};
$('lod').onchange=()=>{$('lodnote').textContent=LN[$('lod').value];analyze();};
$('lodnote').textContent=LN[$('lod').value];
['tsolid','tpts','tfloor','tpins'].forEach(i=>$(i).onchange=vis);
$('mbtn').onclick=()=>{measuring=!measuring;$('mbtn').textContent=measuring?'Measuring... (click floor)':'Measure';};
$('mclr').onclick=()=>{mobj.forEach(o=>{scene.remove(o);o.geometry.dispose();});mobj=[];mpts=[];$('mres').textContent='Measure: click two points on the floor.';};
$('rooms').onclick=e=>{const tr=e.target.closest('tr.rr');if(!tr)return;const r=S.rooms[+tr.dataset.i];
  controls.target.set(r.cx,0,r.cz);camera.position.set(r.cx,S.size*.45,r.cz+S.size*.45);};
$('obj').onclick=()=>ready()&&dl('innoclique_plan.obj',objText());
$('xyz').onclick=()=>{if(!ready())return;const a=S.pts.geometry.attributes.position.array,H=hgt(),o=[];
  for(let i=0;i<a.length;i+=3)o.push(a[i].toFixed(3)+' '+(a[i+1]*H).toFixed(3)+' '+a[i+2].toFixed(3));dl('innoclique_points.xyz',o.join('\n'));};
$('csv').onclick=()=>{if(!ready())return;dl('innoclique_rooms.csv',['Room,Area_m2,Width_m,Depth_m,Centre_x_m,Centre_z_m'].concat(
  S.rooms.map((r,i)=>['Room '+(i+1),r.area.toFixed(2),r.w.toFixed(2),r.d.toFixed(2),r.cx.toFixed(2),r.cz.toFixed(2)].join(','))).join('\n'),'text/csv');};
$('png').onclick=()=>{renderer.render(scene,camera);dl('innoclique_3d.png',renderer.domElement.toDataURL('image/png'));};
})();
"""


# ----------------------- CAD vs REVIT COMPARE TOOL (runs in browser) -------
CMP_CSS = """
.vp{position:relative;height:560px;overflow:hidden;border:1px solid var(--line);border-radius:var(--radius);
background:#fff;cursor:grab;touch-action:none}
.vp .lay{position:absolute;left:0;top:0;transform-origin:0 0}
.vp canvas{display:block;image-rendering:pixelated}
.mk{position:absolute;border:solid #e5484d;border-width:calc(2px / var(--z,1));border-radius:50%;
pointer-events:none;box-sizing:border-box}
.mk b{position:absolute;left:0;top:0;transform:translateY(-100%) scale(calc(1 / var(--z,1)));
transform-origin:0 100%;background:#e5484d;color:#fff;font-size:12px;padding:0 6px;border-radius:6px}
.legend{display:flex;gap:16px;flex-wrap:wrap;font-size:.82rem;color:var(--muted);margin:0 0 10px}
.legend i{display:inline-block;width:12px;height:12px;border-radius:3px;margin-right:6px;vertical-align:-1px}
.layers{max-height:130px;overflow:auto;display:grid;gap:4px}
.ctl input[type=number],.ctl select{padding:8px 10px}
.sev-High{color:#e5484d;font-weight:700}.sev-Medium{color:#d98a00;font-weight:700}.sev-Low{color:var(--muted);font-weight:600}
.cmpt{margin-top:16px}.cmpt h3{margin:18px 0 8px}
"""

CMP_HTML = f"""
<section id="compare"><div class="wrap">
  <div class="eyebrow">Compare</div>
  <h2>CAD vs Revit drawing checker</h2>
  <p class="sub">Upload your CAD file (DXF) and your Revit drawing (PDF, image or DXF export).
  Innoclique aligns them, checks every measurement against the level of development you
  pick, and highlights each mismatch in 2D and in 3D. It runs in your browser and nothing is uploaded.</p>
  <div class="tool">
    <aside class="panel">
      <label class="drop" id="c_dropa"><input type="file" id="c_a" accept=".dxf,.dwg" hidden>
        <b>1. CAD file</b><span class="muted" id="c_asta">DXF (export DWG as ASCII DXF)</span></label>
      <label class="drop" id="c_dropb"><input type="file" id="c_b" accept=".dxf,.pdf,.rvt,image/*" hidden>
        <b>2. Revit drawing</b><span class="muted" id="c_bsta">PDF, PNG, JPG or DXF export</span></label>
      <button class="btn ghost" id="c_sample" type="button">Try a sample pair</button>
      <div id="c_status" class="muted">Waiting for both files...</div>
      <div class="ctl"><label>Level of development (LOD)</label><select id="c_lod">
        <option value="100">LOD 100 - Concept</option><option value="200">LOD 200 - Approximate</option>
        <option value="300" selected>LOD 300 - Precise</option><option value="350">LOD 350 - Coordinated</option>
        <option value="400">LOD 400 - Fabrication</option><option value="500">LOD 500 - As-built</option></select></div>
      <div class="ctl"><label>Tolerance (mm)</label><input type="number" id="c_tol" min="1" value="50"></div>
      <div id="c_lodnote" class="muted"></div>
      <div class="ctl"><label>CAD units</label><select id="c_un"><option value="auto">Auto-detect</option>
        <option value="0.001">Millimetres</option><option value="0.01">Centimetres</option>
        <option value="1">Metres</option><option value="0.0254">Inches</option><option value="0.3048">Feet</option></select></div>
      <div class="ctl"><label>Wall height for 3D (m)</label><input type="number" id="c_h" min="2" max="8" step="0.1" value="2.7"></div>
      {chk("c_al", "Auto-align the two drawings")}
      {chk("c_fit", "Auto-fit PDF/image to CAD size")}
      <div class="ctl"><label>PDF/image real width (m) if not auto-fit</label><input type="number" id="c_bw" value="12" step="0.1" min="0.1"></div>
      <b style="font-size:.85rem">CAD layers to compare</b><div class="layers" id="layers"><span class="muted">Load a CAD file.</span></div>
      {chk("c_sA", "Show CAD-only")}{chk("c_sB", "Show Revit-only")}{chk("c_sM", "Show matching")}{chk("c_sK", "Show markers")}
      <div class="btns"><button class="btn" id="c_csv" type="button">Issues .CSV</button>
        <button class="btn" id="c_png" type="button">Screenshot</button></div>
    </aside>
    <div>
      <div class="legend"><span><i style="background:#e5484d"></i>In CAD, not in Revit</span>
        <span><i style="background:#0c6cf0"></i>In Revit, not in CAD</span>
        <span><i style="background:#94a3b8"></i>Matching</span><span>Scroll to zoom, drag to pan or orbit</span></div>
      <div class="btns" style="margin-bottom:10px"><button class="btn ghost" id="c_m2" type="button">2D</button>
        <button class="btn ghost" id="c_m3" type="button">3D</button>
        <button class="btn" id="c_mb" type="button">2D + 3D</button></div>
      <div class="vp" id="vp"><div class="lay" id="lay"><canvas id="ov"></canvas><div id="mks"></div></div></div>
      <div class="v3d" id="c_v3d" style="display:none;margin-top:14px"></div>
      <div class="stats" id="c_stats"></div>
      <div class="cmpt"><h3>Issues found</h3><div class="tbl-wrap"><table>
        <thead><tr><th>#</th><th>Severity</th><th>Type</th><th>What is different</th></tr></thead>
        <tbody id="c_issues"><tr><td colspan="4" class="muted">Upload both files, or try the sample pair.</td></tr></tbody></table></div>
      <h3>Room measurements</h3><div class="tbl-wrap"><table>
        <thead><tr><th>Room</th><th>CAD</th><th>Revit</th><th>Difference</th><th>Status</th></tr></thead>
        <tbody id="c_rooms"><tr><td colspan="5" class="muted">Rooms are compared from LOD 200 upward.</td></tr></tbody></table></div></div>
    </div>
  </div>
</div></section>
"""

CMP_JS = r"""
(function(){
if(!window.IQ)return;
const $=id=>document.getElementById(id),{otsu,ccl,rectsOf,tag}=window.IQ;
/*PURE_START*/
const LODS={100:[500,0,0],200:[150,0,1],300:[50,1,1],350:[25,1,1],400:[10,1,1],500:[5,1,1]};
const NOTE={100:'Checks overall size only.',200:'Checks overall size and room sizes.',300:'Checks size, rooms and wall geometry.',350:'Same as 300, tighter tolerance.',400:'Same checks, fabrication-level tolerance.',500:'Same checks, as-built tolerance.'};
const SKIP=/(dim|text|anno|note|hatch|furn|grid|defpoints|title|tag|viewport|xref|symbol)/i,UNITS={1:.0254,2:.3048,4:.001,5:.01,6:1};
const sev=r=>r>=10?'High':r>=4?'Medium':'Low';
function parseDXF(txt){
  const L=txt.split(/\r?\n/),ents=[],blocks={};let sec='',want=false,blk=null,cur=null,poly=null,hdr=null,units=null;
  for(let k=0;k+1<L.length;k+=2){
    const c=parseInt(L[k],10),v=L[k+1].trim();if(isNaN(c))continue;
    if(c===9){hdr=v;continue;}
    if(hdr==='$INSUNITS'&&c===70){units=+v;hdr=null;continue;}
    if(c===0){cur=null;
      if(v==='SECTION'){want=true;sec='';}else if(v==='ENDSEC')sec='';else if(v==='EOF')break;
      else if(v==='ENDBLK')blk=null;else if(v==='SEQEND')poly=null;
      else if(v==='BLOCK')cur={t:'BLOCK',g:{},layer:'0'};else if(v==='VERTEX')cur={t:'VERTEX',g:{},layer:'0'};
      else{cur={t:v,g:{},layer:'0'};if(v==='POLYLINE'){cur.vx=[];cur.vy=[];poly=cur;}
        if(sec==='ENTITIES')ents.push(cur);else if(sec==='BLOCKS'&&blk)blk.push(cur);}
      continue;}
    if(!cur){if(c===2&&want){sec=v;want=false;}continue;}
    if(cur.t==='BLOCK'&&c===2){blk=blocks[v]=[];continue;}
    if(cur.t==='VERTEX'&&poly){if(c===10)poly.vx.push(+v);else if(c===20)poly.vy.push(+v);continue;}
    if(c===8)cur.layer=v;else(cur.g[c]||(cur.g[c]=[])).push(v);}
  const segs=[];
  const fl=(list,T,d,ly0)=>{for(const e of list){const g=e.g,ly=(ly0&&e.layer==='0')?ly0:e.layer,n=k=>+g[k][0];
    if(e.t==='LINE'&&g[10]&&g[11]){const p=T(n(10),n(20)),q=T(n(11),n(21));segs.push([p[0],p[1],q[0],q[1],ly]);}
    else if(e.t==='LWPOLYLINE'||e.t==='POLYLINE'){const xs=e.t==='POLYLINE'?e.vx:(g[10]||[]).map(Number),ys=e.t==='POLYLINE'?e.vy:(g[20]||[]).map(Number),m=xs.length,cl=g[70]&&(+g[70][0]&1);
      for(let i=0;i<m-1+(cl?1:0);i++){const p=T(xs[i],ys[i]),q=T(xs[(i+1)%m],ys[(i+1)%m]);segs.push([p[0],p[1],q[0],q[1],ly]);}}
    else if((e.t==='CIRCLE'||e.t==='ARC')&&g[40]){const cx=n(10),cy=n(20),r=n(40),a=e.t==='ARC'?n(50):0,b=e.t==='ARC'?n(51):360,s1=b<=a?b+360:b,N=Math.max(8,Math.ceil((s1-a)/10));let pr=null;
      for(let i=0;i<=N;i++){const t=(a+(s1-a)*i/N)*Math.PI/180,p=T(cx+r*Math.cos(t),cy+r*Math.sin(t));if(pr)segs.push([pr[0],pr[1],p[0],p[1],ly]);pr=p;}}
    else if(e.t==='INSERT'&&d<4&&g[2]&&blocks[g[2][0]]){const sx=g[41]?n(41):1,sy=g[42]?n(42):1,a=(g[50]?n(50):0)*Math.PI/180,co=Math.cos(a),si=Math.sin(a),ix=n(10),iy=n(20);
      fl(blocks[g[2][0]],(x,y)=>T(sx*x*co-sy*y*si+ix,sx*x*si+sy*y*co+iy),d+1,ly);}}};
  fl(ents,(x,y)=>[x,y],0,null);
  const layers={};segs.forEach(s=>layers[s[4]]=(layers[s[4]]||0)+1);
  return{segs,layers,units};}
function unitScale(p,sel){if(sel!=='auto')return +sel;if(UNITS[p.units])return UNITS[p.units];
  let m=0;for(const s of p.segs)m=Math.max(m,Math.abs(s[0]),Math.abs(s[2]));return m>300?.001:1;}
function trim(segs,sc){const xs=segs.map(s=>(s[0]+s[2])/2*sc).sort((a,b)=>a-b),ys=segs.map(s=>(s[1]+s[3])/2*sc).sort((a,b)=>a-b),n=xs.length,
  q=(a,p)=>a[Math.min(n-1,Math.max(0,Math.floor(p*(n-1))))],mx=(q(xs,.995)-q(xs,.005))*.1,my=(q(ys,.995)-q(ys,.005))*.1,
  lx=q(xs,.005)-mx,hx=q(xs,.995)+mx,ly=q(ys,.005)-my,hy=q(ys,.995)+my;
  const out=segs.filter(s=>{const x=(s[0]+s[2])/2*sc,y=(s[1]+s[3])/2*sc;return x>=lx&&x<=hx&&y>=ly&&y<=hy;});
  let x0=1e18,x1=-1e18,y0=1e18,y1=-1e18;
  for(const s of out)for(const k of[0,2]){x0=Math.min(x0,s[k]*sc);x1=Math.max(x1,s[k]*sc);y0=Math.min(y0,s[k+1]*sc);y1=Math.max(y1,s[k+1]*sc);}
  return{segs:out,bb:{x0,x1,y0,y1}};}
function rasterSegs(segs,sc,bb,cell,W,H,pad){const m=new Uint8Array(W*H),X=x=>Math.round((x*sc-bb.x0)/cell)+pad,Y=y=>Math.round((bb.y1-y*sc)/cell)+pad;
  for(const s of segs){let x0=X(s[0]),y0=Y(s[1]);const x1=X(s[2]),y1=Y(s[3]),dx=Math.abs(x1-x0),dy=-Math.abs(y1-y0),sx=x0<x1?1:-1,sy=y0<y1?1:-1;let e=dx+dy;
    for(;;){if(x0>=0&&x0<W&&y0>=0&&y0<H)m[y0*W+x0]=1;if(x0===x1&&y0===y1)break;const e2=2*e;if(e2>=dy){e+=dy;x0+=sx;}if(e2<=dx){e+=dx;y0+=sy;}}}
  return m;}
function dil(m,W,H,r){if(r<1)return m;const t=new Uint8Array(m.length),o=new Uint8Array(m.length),c=new Int32Array(Math.max(W,H)+1);
  for(let y=0;y<H;y++){c[0]=0;for(let x=0;x<W;x++)c[x+1]=c[x]+m[y*W+x];for(let x=0;x<W;x++)t[y*W+x]=c[Math.min(W,x+r+1)]-c[Math.max(0,x-r)]>0?1:0;}
  for(let x=0;x<W;x++){c[0]=0;for(let y=0;y<H;y++)c[y+1]=c[y]+t[y*W+x];for(let y=0;y<H;y++)o[y*W+x]=c[Math.min(H,y+r+1)]-c[Math.max(0,y-r)]>0?1:0;}
  return o;}
function edge(m,W,H){const o=new Uint8Array(m.length);
  for(let y=0;y<H;y++)for(let x=0;x<W;x++){const p=y*W+x;if(m[p]&&(x===0||y===0||x===W-1||y===H-1||!m[p-1]||!m[p+1]||!m[p-W]||!m[p+W]))o[p]=1;}return o;}
function shiftMask(m,W,H,dx,dy){const o=new Uint8Array(m.length);
  for(let y=0;y<H;y++)for(let x=0;x<W;x++)if(m[y*W+x]){const X=x+dx,Y=y+dy;if(X>=0&&Y>=0&&X<W&&Y<H)o[Y*W+X]=1;}return o;}
function align(a,b,W,H){const f=4,w=Math.ceil(W/f),h=Math.ceil(H/f);
  const pool=m=>{const o=new Uint8Array(w*h);for(let y=0;y<H;y++)for(let x=0;x<W;x++)if(m[y*W+x])o[((y/f)|0)*w+((x/f)|0)]=1;return o;};
  const pts=(m,mw,mh,cap)=>{const P=[];for(let i=0;i<mw*mh;i++)if(m[i])P.push(i%mw,(i/mw)|0);const st=Math.max(1,Math.floor(P.length/2/cap)),o=[];for(let j=0;j<P.length/2;j+=st)o.push(P[2*j],P[2*j+1]);return o;};
  const best=(P,Q,pw,ph,R,cx,cy)=>{let bs=-1,bx=cx,by=cy;
    for(let sy=cy-R;sy<=cy+R;sy++)for(let sx=cx-R;sx<=cx+R;sx++){let s=0;for(let i=0;i<P.length;i+=2){const x=P[i]-sx,y=P[i+1]-sy;if(x>=0&&y>=0&&x<pw&&y<ph&&Q[y*pw+x])s++;}if(s>bs){bs=s;bx=sx;by=sy;}}return[bx,by];};
  const c=best(pts(pool(a),w,h,3000),dil(pool(b),w,h,1),w,h,Math.min(30,(w/5)|0),0,0);
  return best(pts(a,W,H,4000),dil(b,W,H,1),W,H,5,c[0]*f,c[1]*f);}
function rooms(m,W,H,cell){const f=4,w=Math.ceil(W/f),h=Math.ceil(H/f),c=new Uint8Array(w*h);
  for(let y=0;y<H;y++)for(let x=0;x<W;x++)if(m[y*W+x])c[((y/f)|0)*w+((x/f)|0)]=1;
  const cc=cell*f,g=Math.ceil(.55/cc),lab=ccl(dil(c,w,h,g),w,h,0).lab,ext=new Set();
  for(let x=0;x<w;x++){ext.add(lab[x]);ext.add(lab[(h-1)*w+x]);}for(let y=0;y<h;y++){ext.add(lab[y*w]);ext.add(lab[y*w+w-1]);}
  for(let it=0;it<g;it++){const nl=lab.slice();for(let y=0;y<h;y++)for(let x=0;x<w;x++){const p=y*w+x;if(lab[p]||c[p])continue;
    const v=(x>0&&lab[p-1])||(x<w-1&&lab[p+1])||(y>0&&lab[p-w])||(y<h-1&&lab[p+w]);if(v)nl[p]=v;}lab.set(nl);}
  const R={};for(let p=0;p<w*h;p++){const id=lab[p];if(!id||ext.has(id))continue;const x=p%w,y=(p/w)|0,r=R[id]||(R[id]={n:0,sx:0,sy:0,x0:w,x1:0,y0:h,y1:0});
    r.n++;r.sx+=x;r.sy+=y;r.x0=Math.min(r.x0,x);r.x1=Math.max(r.x1,x);r.y0=Math.min(r.y0,y);r.y1=Math.max(r.y1,y);}
  return Object.values(R).filter(r=>r.n*cc*cc>=1).map(r=>({area:r.n*cc*cc,w:(r.x1-r.x0+1)*cc,d:(r.y1-r.y0+1)*cc,gx:(r.sx/r.n+.5)*f,gy:(r.sy/r.n+.5)*f,gw:(r.x1-r.x0+1)*f,gh:(r.y1-r.y0+1)*f})).sort((a,b)=>a.gy-b.gy||a.gx-b.gx);}
function dist(m,W,H){const d=new Int32Array(W*H).fill(1e9);
  for(let y=0;y<H;y++)for(let x=0;x<W;x++){const p=y*W+x;if(m[p])d[p]=0;else{if(x>0&&d[p-1]+1<d[p])d[p]=d[p-1]+1;if(y>0&&d[p-W]+1<d[p])d[p]=d[p-W]+1;}}
  for(let y=H-1;y>=0;y--)for(let x=W-1;x>=0;x--){const p=y*W+x;if(x<W-1&&d[p+1]+1<d[p])d[p]=d[p+1]+1;if(y<H-1&&d[p+W]+1<d[p])d[p]=d[p+W]+1;}
  return d;}
function core(mA,mB,W,H,cell,tolM,lod,doAlign){
  let sh=[0,0];if(doAlign){sh=align(mA,mB,W,H);mB=shiftMask(mB,W,H,sh[0],sh[1]);}
  const tolE=Math.max(tolM,1.5*cell),r=Math.max(1,Math.round(tolE/cell)),eA=edge(mA,W,H),eB=edge(mB,W,H),dA=dil(eA,W,H,r),dB=dil(eB,W,H,r),
    miss=new Uint8Array(W*H),extra=new Uint8Array(W*H);let nA=0,nB=0,kA=0,kB=0;
  for(let i=0;i<miss.length;i++){if(eA[i]){nA++;if(dB[i])kA++;else miss[i]=1;}if(eB[i]){nB++;if(dA[i])kB++;else extra[i]=1;}}
  const issues=[],bbx=m=>{let x0=W,x1=-1,y0=H,y1=-1;for(let i=0;i<m.length;i++)if(m[i]){const x=i%W,y=(i/W)|0;if(x<x0)x0=x;if(x>x1)x1=x;if(y<y0)y0=y;if(y>y1)y1=y;}return x1<0?null:{x0,x1,y0,y1};};
  const fa=bbx(mA),fb=bbx(mB);let fp=null;
  if(fa&&fb){const wa=(fa.x1-fa.x0+1)*cell,da=(fa.y1-fa.y0+1)*cell,wb=(fb.x1-fb.x0+1)*cell,db=(fb.y1-fb.y0+1)*cell,mx=Math.max(Math.abs(wb-wa),Math.abs(db-da));
    fp={wa,da,wb,db};if(mx>tolE)issues.push({kind:'Footprint',sev:sev(mx/tolE),txt:'Overall size: CAD '+wa.toFixed(2)+' x '+da.toFixed(2)+' m, Revit '+wb.toFixed(2)+' x '+db.toFixed(2)+' m',gx:(fa.x0+fa.x1)/2,gy:(fa.y0+fa.y1)/2,gr:Math.max(fa.x1-fa.x0,fa.y1-fa.y0)/2});}
  let ra=[],rb=[];const rows=[];
  if(lod[2]){ra=rooms(mA,W,H,cell);rb=rooms(mB,W,H,cell);const tr=Math.max(tolE,6*cell),used=new Set();
    ra.forEach((a,i)=>{let bj=-1,bd=1e18;rb.forEach((b,j)=>{if(used.has(j))return;const d=Math.hypot(a.gx-b.gx,a.gy-b.gy)*cell;if(d<bd){bd=d;bj=j;}});
      const gr=Math.max(a.gw,a.gh)/2;
      if(bj<0||bd>Math.max(1.5,.35*Math.sqrt(a.area))){rows.push({n:i+1,a,b:null,st:'Missing in Revit'});issues.push({kind:'Room',sev:'High',txt:'Room '+(i+1)+' ('+a.area.toFixed(1)+' m2) exists in CAD but not in Revit',gx:a.gx,gy:a.gy,gr});return;}
      used.add(bj);const b=rb[bj],dw=b.w-a.w,dd=b.d-a.d,mx=Math.max(Math.abs(dw),Math.abs(dd)),bad=mx>tr;rows.push({n:i+1,a,b,dw,dd,st:bad?'Mismatch':'OK'});
      if(bad)issues.push({kind:'Room',sev:sev(mx/tr),txt:'Room '+(i+1)+': CAD '+a.w.toFixed(2)+' x '+a.d.toFixed(2)+' m ('+a.area.toFixed(1)+' m2), Revit '+b.w.toFixed(2)+' x '+b.d.toFixed(2)+' m ('+b.area.toFixed(1)+' m2)',gx:a.gx,gy:a.gy,gr});});
    rb.forEach((b,j)=>{if(!used.has(j)){rows.push({n:'-',a:null,b,st:'Extra in Revit'});issues.push({kind:'Room',sev:'High',txt:'Room of '+b.area.toFixed(1)+' m2 exists in Revit but not in CAD',gx:b.gx,gy:b.gy,gr:Math.max(b.gw,b.gh)/2});}});}
  if(lod[1]){const u=new Uint8Array(W*H);for(let i=0;i<u.length;i++)u[i]=miss[i]|extra[i];
    const lab=ccl(dil(u,W,H,Math.max(3,Math.round(.35/cell))),W,H,1).lab,K={},dTA=dist(eA,W,H),dTB=dist(eB,W,H);
    for(let i=0;i<u.length;i++)if(u[i]){const id=lab[i],x=i%W,y=(i/W)|0,c=K[id]||(K[id]={a:0,b:0,d:[],x0:W,x1:0,y0:H,y1:0});
      if(miss[i]){c.a++;c.d.push(dTB[i]);}else{c.b++;c.d.push(dTA[i]);}
      if(x<c.x0)c.x0=x;if(x>c.x1)c.x1=x;if(y<c.y0)c.y0=y;if(y>c.y1)c.y1=y;}
    Object.values(K).forEach(c=>{const sz=Math.max(c.x1-c.x0,c.y1-c.y0)*cell;if(sz<Math.max(2*tolE,.1))return;let txt,dev=sz;
      if(Math.min(c.a,c.b)>.3*Math.max(c.a,c.b)){c.d.sort((p,q)=>p-q);dev=Math.max(c.d[Math.floor(.9*(c.d.length-1))]*cell,tolE);txt='Linework offset by about '+dev.toFixed(2)+' m (feature about '+sz.toFixed(2)+' m long)';}
      else if(c.a>c.b)txt='CAD linework (about '+sz.toFixed(2)+' m) not found in Revit';else txt='Revit linework (about '+sz.toFixed(2)+' m) not found in CAD';
      issues.push({kind:'Geometry',sev:sev(dev/tolE),txt,gx:(c.x0+c.x1)/2,gy:(c.y0+c.y1)/2,gr:Math.max(sz/cell/2,14)});});}
  const o={High:0,Medium:1,Low:2};issues.sort((a,b)=>o[a.sev]-o[b.sev]);
  return{sh,tolE,score:(nA+nB)?(kA+kB)/(nA+nB):1,issues,rows,fp,eA,eB,miss,extra,ra,rb};}
function sampleDXF(rev){
  const A=[[0,0,12000,200],[0,7800,12000,8000],[0,200,200,7800],[11800,200,12000,7800],[5000,200,5200,3000],[5000,3900,5200,7800],[200,3900,2000,4100],[2900,3900,5000,4100],[5200,3000,8000,3200],[8900,3000,11800,3200]];
  const B=[[0,0,12000,200],[0,7800,12000,8000],[0,200,200,7800],[11800,200,12000,7800],[5300,200,5500,3000],[5300,3900,5500,7800],[200,3900,2000,4100],[2900,3900,5300,4100],[5500,3000,8000,3200],[8900,3000,10000,3200],[9000,200,9200,1600]];
  let s='0\nSECTION\n2\nENTITIES\n';const L=(a,b,c,d,ly)=>{s+='0\nLINE\n8\n'+ly+'\n10\n'+a+'\n20\n'+b+'\n11\n'+c+'\n21\n'+d+'\n';};
  (rev?B:A).forEach(r=>{const[a,b,c,d]=r;L(a,b,c,b,'A-WALL');L(c,b,c,d,'A-WALL');L(c,d,a,d,'A-WALL');L(a,d,a,b,'A-WALL');});
  L(0,-1500,12000,-1500,'A-DIMENSIONS');return s+'0\nENDSEC\n0\nEOF\n';}
/*PURE_END*/
const C={a:null,b:null,on:new Set(),res:null,W:0,H:0,cell:1,disp:null};
let z=1,tx=0,ty=0,tm;const vp=$('vp'),lay=$('lay'),ov=$('ov');
const status=(t,e)=>{const s=$('c_status');s.textContent=t;s.style.color=e?'#e5484d':'';};
function view(){lay.style.transform='translate('+tx+'px,'+ty+'px) scale('+z+')';lay.style.setProperty('--z',z);}
function fit(){if(vp.clientWidth===0)return;z=Math.min(vp.clientWidth/C.W,vp.clientHeight/C.H);tx=(vp.clientWidth-C.W*z)/2;ty=(vp.clientHeight-C.H*z)/2;view();}
vp.addEventListener('wheel',e=>{e.preventDefault();const r=vp.getBoundingClientRect(),mx=e.clientX-r.left,my=e.clientY-r.top,k=e.deltaY<0?1.15:1/1.15;tx=mx-(mx-tx)*k;ty=my-(my-ty)*k;z*=k;view();},{passive:false});
let dr=null;vp.addEventListener('pointerdown',e=>{dr=[e.clientX-tx,e.clientY-ty];vp.setPointerCapture(e.pointerId);vp.style.cursor='grabbing';});
vp.addEventListener('pointermove',e=>{if(dr){tx=e.clientX-dr[0];ty=e.clientY-dr[1];view();}});
vp.addEventListener('pointerup',()=>{dr=null;vp.style.cursor='grab';});
function focus(i){const s=C.res.issues[i];if(C.is3d)fly3D(s);if(C.mode==='3d')return;z=Math.min(vp.clientWidth,vp.clientHeight)/Math.max(s.gr*6,160);tx=vp.clientWidth/2-s.gx*z;ty=vp.clientHeight/2-s.gy*z;view();}

async function rasterFile(f){let cv;
  if(f.type==='application/pdf'||/\.pdf$/i.test(f.name)){if(!window.pdfjsLib)throw new Error('PDF reader not loaded (check internet).');
    pdfjsLib.GlobalWorkerOptions.workerSrc='https://cdn.jsdelivr.net/npm/pdfjs-dist@3.11.174/build/pdf.worker.min.js';
    const pdf=await pdfjsLib.getDocument({data:await f.arrayBuffer()}).promise,pg=await pdf.getPage(1),v0=pg.getViewport({scale:1}),vp0=pg.getViewport({scale:1800/Math.max(v0.width,v0.height)});
    cv=document.createElement('canvas');cv.width=vp0.width;cv.height=vp0.height;const x=cv.getContext('2d');x.fillStyle='#fff';x.fillRect(0,0,cv.width,cv.height);
    await pg.render({canvasContext:x,viewport:vp0}).promise;}
  else{const img=await new Promise((res,rej)=>{const i=new Image();i.onload=()=>res(i);i.onerror=()=>rej(new Error('Not a readable image'));i.src=URL.createObjectURL(f);});
    const sc=Math.min(1,1800/Math.max(img.width,img.height));cv=document.createElement('canvas');cv.width=Math.round(img.width*sc);cv.height=Math.round(img.height*sc);
    const x=cv.getContext('2d');x.fillStyle='#fff';x.fillRect(0,0,cv.width,cv.height);x.drawImage(img,0,0,cv.width,cv.height);}
  return cv;}
async function read(f){const n=f.name;
  if(/\.dwg$/i.test(n))throw new Error('DWG is a closed binary format. Export it from your CAD tool as ASCII DXF and upload that.');
  if(/\.rvt$/i.test(n))throw new Error('.rvt cannot be opened in a browser. In Revit use Export > CAD Formats > DXF, or export the sheet to PDF or an image.');
  if(/\.dxf$/i.test(n)){const t=await f.text();if(t.indexOf('\0')>=0||/^AutoCAD Binary/.test(t))throw new Error('This is a binary DXF. Save it as ASCII DXF.');
    const p=parseDXF(t);if(!p.segs.length)throw new Error('No lines found. Only lines, polylines, arcs, circles and blocks are read.');return p;}
  return{cv:await rasterFile(f)};}
function prep(cv){const w=cv.width,h=cv.height,d=cv.getContext('2d').getImageData(0,0,w,h).data,g=new Uint8Array(w*h);let s=0;
  for(let i=0;i<w*h;i++){g[i]=(d[i*4]*.3+d[i*4+1]*.59+d[i*4+2]*.11)|0;s+=g[i];}
  const hs=new Array(256).fill(0);if(s/(w*h)<110)for(let i=0;i<g.length;i++)g[i]=255-g[i];
  for(let i=0;i<g.length;i++)hs[g[i]]++;const t=Math.min(250,otsu(hs,w*h)+1),bc=document.createElement('canvas');bc.width=w;bc.height=h;
  const x=bc.getContext('2d'),im=x.createImageData(w,h);let x0=w,x1=0,y0=h,y1=0;
  for(let i=0;i<w*h;i++){const v=g[i]<t?0:255,q=i*4;im.data[q]=im.data[q+1]=im.data[q+2]=v;im.data[q+3]=255;
    if(!v){const px=i%w,py=(i/w)|0;if(px<x0)x0=px;if(px>x1)x1=px;if(py<y0)y0=py;if(py>y1)y1=py;}}
  x.putImageData(im,0,0);return{bc,bx:x0,by:y0,bw:x1-x0+1,bh:y1-y0+1};}
function drawPrep(p,cell,W,H,pad){const c=document.createElement('canvas');c.width=W;c.height=H;const x=c.getContext('2d');x.fillStyle='#fff';x.fillRect(0,0,W,H);
  const s=p.mpp/cell;x.drawImage(p.bc,p.bx,p.by,p.bw,p.bh,pad,pad,p.bw*s,p.bh*s);const d=x.getImageData(0,0,W,H).data,m=new Uint8Array(W*H);
  for(let i=0;i<m.length;i++)if(d[i*4]<225)m[i]=1;return m;}

function run(){
  if(!C.a||!C.b){status('Waiting for both files...');return;}
  try{const sel=$('c_un').value,lodv=$('c_lod').value,lod=LODS[lodv],tol=Math.max(1,+$('c_tol').value||50)/1000,PAD=40;
    const scA=unitScale(C.a,sel),A=trim(C.a.segs.filter(s=>C.on.has(s[4])),scA);
    if(!A.segs.length)throw new Error('No CAD lines in the selected layers.');
    const Aw=A.bb.x1-A.bb.x0,Ah=A.bb.y1-A.bb.y0,cell=Math.max(Aw,Ah)/1400;let B,scB,pr=null,Bw,Bh;
    if(C.b.segs){scB=unitScale(C.b,sel);B=trim(C.b.segs.filter(s=>!SKIP.test(s[4])),scB);if(!B.segs.length)throw new Error('No usable lines in the Revit DXF.');Bw=B.bb.x1-B.bb.x0;Bh=B.bb.y1-B.bb.y0;}
    else{pr=prep(C.b.cv);pr.mpp=($('c_fit').checked?Aw:(+$('c_bw').value||Aw))/pr.bw;Bw=pr.bw*pr.mpp;Bh=pr.bh*pr.mpp;}
    const W=Math.ceil(Math.max(Aw,Bw)/cell)+2*PAD,H=Math.ceil(Math.max(Ah,Bh)/cell)+2*PAD;
    if(Math.max(W,H)>3000)throw new Error('The drawings differ hugely in size. Check the CAD units or turn on auto-fit.');
    const mA=rasterSegs(A.segs,scA,A.bb,cell,W,H,PAD),mB=pr?drawPrep(pr,cell,W,H,PAD):rasterSegs(B.segs,scB,B.bb,cell,W,H,PAD);
    const r=core(mA,mB,W,H,cell,tol,lod,$('c_al').checked);
    Object.assign(C,{res:r,W,H,cell,disp:{m:dil(r.miss,W,H,1),x:dil(r.extra,W,H,1)}});render(r.sh[0]===0&&r.sh[1]===0);
  }catch(e){status('Error: '+e.message,true);console.error(e);}}

function paint(){const r=C.res,W=C.W,H=C.H;ov.width=W;ov.height=H;const x=ov.getContext('2d'),im=x.createImageData(W,H),d=im.data,sA=$('c_sA').checked,sB=$('c_sB').checked,sM=$('c_sM').checked;
  for(let i=0;i<W*H;i++){let c=null;if(C.disp.m[i]&&sA)c=[229,72,77];else if(C.disp.x[i]&&sB)c=[12,108,240];else if(sM&&(r.eA[i]||r.eB[i]))c=[148,163,184];
    if(c){const q=i*4;d[q]=c[0];d[q+1]=c[1];d[q+2]=c[2];d[q+3]=255;}}
  x.putImageData(im,0,0);$('mks').style.display=$('c_sK').checked?'block':'none';}
function render(){const r=C.res,cell=C.cell;paint();
  $('mks').innerHTML=r.issues.map((s,i)=>'<div class="mk" style="left:'+(s.gx-s.gr)+'px;top:'+(s.gy-s.gr)+'px;width:'+2*s.gr+'px;height:'+2*s.gr+'px"><b>'+(i+1)+'</b></div>').join('');
  const n=k=>r.issues.filter(s=>s.sev===k).length,mm=v=>(v*1000).toFixed(0)+' mm',ok=r.rows.filter(w=>w.st==='OK').length;
  const st=[['Match score',(r.score*100).toFixed(1)+'%'],['Issues',r.issues.length],['High / Med / Low',n('High')+' / '+n('Medium')+' / '+n('Low')],
    ['Rooms OK',r.rows.length?ok+' of '+r.rows.length:'n/a'],['Footprint (CAD)',r.fp?r.fp.wa.toFixed(1)+' x '+r.fp.da.toFixed(1)+' m':'-'],
    ['Tolerance used',mm(r.tolE)],['Grid resolution',mm(cell)+' / px'],['Auto-align shift',mm(Math.hypot(r.sh[0],r.sh[1])*cell)]];
  $('c_stats').innerHTML=st.map(a=>'<div class="card"><div class="muted">'+a[0]+'</div><h3>'+a[1]+'</h3></div>').join('');
  $('c_issues').innerHTML=r.issues.length?r.issues.map((s,i)=>'<tr class="rr" data-i="'+i+'"><td>'+(i+1)+'</td><td class="sev-'+s.sev+'">'+s.sev+'</td><td>'+s.kind+'</td><td>'+s.txt+'</td></tr>').join(''):
    '<tr><td colspan="4"><b>No mismatches above the tolerance.</b></td></tr>';
  const f=v=>(v>=0?'+':'')+v.toFixed(2);
  $('c_rooms').innerHTML=r.rows.length?r.rows.map(w=>'<tr><td>'+w.n+'</td><td>'+(w.a?w.a.area.toFixed(1)+' m2 ('+w.a.w.toFixed(2)+' x '+w.a.d.toFixed(2)+')':'-')+'</td><td>'+(w.b?w.b.area.toFixed(1)+' m2 ('+w.b.w.toFixed(2)+' x '+w.b.d.toFixed(2)+')':'-')+'</td><td>'+(w.dw!==undefined?f(w.dw)+' x '+f(w.dd)+' m':'-')+'</td><td class="'+(w.st==='OK'?'':'sev-High')+'">'+w.st+'</td></tr>').join(''):
    '<tr><td colspan="5" class="muted">Rooms are compared from LOD 200 upward.</td></tr>';
  status('Compared. '+r.issues.length+' issue(s) found. Click a row to zoom to it.');fit();V.dirty=true;setMode(C.mode||'both');}

async function load(w,f){if(!f)return;try{status('Reading '+f.name+' ...');const r=await read(f);
  if(w==='a'&&!r.segs)throw new Error('The CAD file must be a DXF.');C[w]=r;
  $('c_'+w+'sta').textContent=f.name+(r.segs?' - '+r.segs.length+' line segments':' - image/PDF');if(w==='a')layersUI();run();}
  catch(e){status('Error: '+e.message,true);}}
function layersUI(){C.on=new Set();const L=C.a.layers;
  $('layers').innerHTML=Object.keys(L).map(k=>{const on=!SKIP.test(k);if(on)C.on.add(k);return'<label class="chk"><input type="checkbox" data-l="'+k.replace(/"/g,'')+'"'+(on?' checked':'')+'> '+k+' ('+L[k]+')</label>';}).join('');}
function sample(){C.a=parseDXF(sampleDXF(false));C.b=parseDXF(sampleDXF(true));$('c_asta').textContent='Sample CAD (DXF)';$('c_bsta').textContent='Sample Revit export (DXF) with 3 planted errors';layersUI();run();}
function note(){const v=$('c_lod').value;$('c_lodnote').textContent=NOTE[v]+' Default tolerance '+LODS[v][0]+' mm; you can change it.';}

[['a','c_a'],['b','c_b']].forEach(([w,id])=>{$(id).onchange=e=>load(w,e.target.files[0]);const dz=$('c_drop'+w);
  dz.ondragover=e=>{e.preventDefault();dz.classList.add('on');};dz.ondragleave=()=>dz.classList.remove('on');dz.ondrop=e=>{e.preventDefault();dz.classList.remove('on');load(w,e.dataTransfer.files[0]);};});
$('c_sample').onclick=sample;
$('c_lod').onchange=()=>{$('c_tol').value=LODS[$('c_lod').value][0];note();run();};
['c_tol','c_bw'].forEach(i=>$(i).oninput=()=>{clearTimeout(tm);tm=setTimeout(run,300);});
['c_un','c_al','c_fit'].forEach(i=>$(i).onchange=run);
['c_sA','c_sB','c_sM','c_sK'].forEach(i=>$(i).onchange=()=>C.res&&paint());
$('layers').onchange=e=>{const l=e.target.dataset.l;if(!l)return;e.target.checked?C.on.add(l):C.on.delete(l);run();};
$('c_issues').onclick=e=>{const tr=e.target.closest('tr.rr');if(tr)focus(+tr.dataset.i);};
$('c_csv').onclick=()=>{if(!C.res)return;const q=s=>'"'+String(s).replace(/"/g,'""')+'"',cell=C.cell;
  const t=['No,Severity,Type,Description,X_m,Y_m'].concat(C.res.issues.map((s,i)=>[i+1,s.sev,s.kind,q(s.txt),(s.gx*cell).toFixed(2),(s.gy*cell).toFixed(2)].join(','))).join('\n');
  const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([t],{type:'text/csv'}));a.download='innoclique_issues.csv';a.click();};
$('c_png').onclick=()=>{if(!C.res)return;const c=document.createElement('canvas');c.width=C.W;c.height=C.H;const x=c.getContext('2d');x.fillStyle='#fff';x.fillRect(0,0,C.W,C.H);x.drawImage(ov,0,0);
  x.lineWidth=3;x.strokeStyle='#e5484d';x.fillStyle='#e5484d';x.font='bold 16px sans-serif';
  C.res.issues.forEach((s,i)=>{x.beginPath();x.arc(s.gx,s.gy,s.gr,0,6.283);x.stroke();x.fillText(i+1,s.gx-s.gr,s.gy-s.gr-4);});
  const a=document.createElement('a');a.href=c.toDataURL('image/png');a.download='innoclique_comparison.png';a.click();};

/* ---------- 3D view of the comparison ---------- */
const V={r:null,sc:null,cam:null,ctl:null,dyn:[],dirty:true};C.mode=null;C.is3d=false;
const hgt3=()=>Math.max(.5,+$('c_h').value||2.7);
function init3(){if(V.r||!window.THREE)return;const el=$('c_v3d');V.sc=new THREE.Scene();V.cam=new THREE.PerspectiveCamera(50,1,.1,5000);
  V.r=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true,alpha:true});el.appendChild(V.r.domElement);
  V.ctl=new THREE.OrbitControls(V.cam,V.r.domElement);V.ctl.enableDamping=true;V.sc.add(new THREE.HemisphereLight(0xffffff,0x445566,.95));
  const d=new THREE.DirectionalLight(0xffffff,.8);d.position.set(5,10,6);V.sc.add(d);
  (function loop(){requestAnimationFrame(loop);if(C.is3d){V.ctl.update();V.r.render(V.sc,V.cam);}})();addEventListener('resize',rs3);}
function rs3(){if(!V.r)return;const el=$('c_v3d'),w=el.clientWidth,h=el.clientHeight;if(!w)return;V.r.setSize(w,h);V.cam.aspect=w/h;V.cam.updateProjectionMatrix();}
function setMode(m){C.mode=m;C.is3d=m!=='2d';$('vp').style.display=m==='3d'?'none':'';$('c_v3d').style.display=C.is3d?'block':'none';
  ['2','3','b'].forEach(k=>$('c_m'+k).className='btn'+((k==='2'&&m==='2d')||(k==='3'&&m==='3d')||(k==='b'&&m==='both')?'':' ghost'));
  if(C.is3d&&C.res){init3();rs3();if(V.dirty)build3D();}if(!C.is3d||m==='both')setTimeout(()=>{if(C.res)fit();},0);}
function boxes(mask,color,hf){const rc=rectsOf(mask,C.W,C.H);if(!rc.length)return;const c=C.cell,hh=hgt3()*hf,
  mesh=new THREE.InstancedMesh(new THREE.BoxGeometry(1,1,1),new THREE.MeshStandardMaterial({color,roughness:.8}),rc.length),m4=new THREE.Matrix4(),q=new THREE.Quaternion();
  rc.forEach((r,i)=>{m4.compose(new THREE.Vector3((r.x+r.w/2-C.W/2)*c,hh/2,(r.y+r.h/2-C.H/2)*c),q,new THREE.Vector3(r.w*c,hh,r.h*c));mesh.setMatrixAt(i,m4);});
  V.sc.add(mesh);V.dyn.push(mesh);}
function build3D(){if(!V.r||!C.res)return;const r=C.res,W=C.W,H=C.H,c=C.cell,n=W*H,k=Math.max(1,Math.round(.04/c)),size=Math.max(W,H)*c,h=hgt3();
  V.dyn.forEach(o=>{V.sc.remove(o);if(o.geometry)o.geometry.dispose();if(o.material){if(o.material.map)o.material.map.dispose();o.material.dispose();}});V.dyn=[];
  const mt=new Uint8Array(n),mi=new Uint8Array(n),ex=new Uint8Array(n);
  for(let i=0;i<n;i++){if(r.miss[i])mi[i]=1;else if(r.extra[i])ex[i]=1;else if(r.eA[i]||r.eB[i])mt[i]=1;}
  const fl=new THREE.Mesh(new THREE.PlaneGeometry(W*c,H*c),new THREE.MeshBasicMaterial({color:0xf1f5f9}));fl.rotation.x=-Math.PI/2;fl.position.y=-.01;V.sc.add(fl);V.dyn.push(fl);
  if($('c_sM').checked)boxes(dil(mt,W,H,k),0x94a3b8,1);
  if($('c_sA').checked)boxes(dil(mi,W,H,k+1),0xe5484d,1.12);
  if($('c_sB').checked)boxes(dil(ex,W,H,k+1),0x0c6cf0,1.12);
  if($('c_sK').checked)r.issues.forEach((s,i)=>{const col={High:0xe5484d,Medium:0xf09c00,Low:0x64748b}[s.sev],rad=Math.max(s.gr*c,.3),
    ring=new THREE.Mesh(new THREE.CylinderGeometry(rad,rad,h*1.3,32,1,true),new THREE.MeshBasicMaterial({color:col,transparent:true,opacity:.22,side:THREE.DoubleSide,depthWrite:false}));
    ring.position.set((s.gx-W/2)*c,h*.65,(s.gy-H/2)*c);V.sc.add(ring);V.dyn.push(ring);
    const t=tag('#'+(i+1)+' '+s.sev);t.scale.set(size*.12,size*.12*80/300,1);t.position.set((s.gx-W/2)*c,h*1.5,(s.gy-H/2)*c);V.sc.add(t);V.dyn.push(t);});
  V.size=size;V.cam.position.set(0,size*.9,size*.8);V.ctl.target.set(0,0,0);V.dirty=false;}
function fly3D(s){if(!V.r||!C.res)return;if(V.dirty)build3D();const c=C.cell,x=(s.gx-C.W/2)*c,z=(s.gy-C.H/2)*c,d=Math.max(s.gr*c*4,V.size*.12);
  V.ctl.target.set(x,0,z);V.cam.position.set(x,d,z+d);}
$('c_m2').onclick=()=>setMode('2d');$('c_m3').onclick=()=>setMode('3d');$('c_mb').onclick=()=>setMode('both');
['c_sA','c_sB','c_sM','c_sK'].forEach(i=>$(i).addEventListener('change',()=>{V.dirty=true;if(C.is3d)build3D();}));
$('c_h').addEventListener('input',()=>{V.dirty=true;if(C.is3d&&C.res){clearTimeout(tm);tm=setTimeout(build3D,200);}});
{const op=$('c_png').onclick;$('c_png').onclick=()=>{if(C.mode==='3d'&&V.r){V.r.render(V.sc,V.cam);const a=document.createElement('a');a.href=V.r.domElement.toDataURL('image/png');a.download='innoclique_comparison_3d.png';a.click();}else op();};}

note();
})();
"""


# ----------------------------- HTML BUILDERS ------------------------------
def product_cards():
    return "\n".join(
        f"""<a class="card" href="{escape(p["link"])}">
  <h3>{escape(p['name'])}</h3><div class="tag">{escape(p['kind'])}</div>
  <p class="muted">{escape(p['desc'])}</p>
  <p class="muted" style="margin-top:10px"><strong>{escape(p['formats'])}</strong></p>
  <p style="margin-top:14px;color:var(--accent)">See {escape(p['name'])} &rarr;</p></a>"""
        for p in PRODUCTS)


FORMATS = ("PDF", "DXF", "CSV", "GEOJSON", "IFC", "REVIT")


def deliverable_rows():
    rows = []
    for what, formats, who in DELIVERABLES:
        pills = " ".join(
            f"<code>{escape(f)}</code>" if f.split()[0].upper() in FORMATS
            else f"<span class='muted'>{escape(f)}</span>"
            for f in formats)
        rows.append(f"<tr><td><strong>{escape(what)}</strong></td>"
                    f"<td>{pills}</td><td class='muted'>{escape(who)}</td></tr>")
    return "\n".join(rows)


def build_html():
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{SITE['name']}. CAD vs Revit drawing checker.</title>
<meta name="description" content="{escape(SITE['intro'])}">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Ccircle cx='16' cy='16' r='9' fill='%23f09c00'/%3E%3Ccircle cx='16' cy='16' r='14' fill='none' stroke='%230c6cf0' stroke-width='3'/%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>{CSS}{TOOL_CSS}{CMP_CSS}</style>
</head>
<body>
<header><div class="wrap"><nav>
  <a class="logo" href="#top"><img src="{LOGO}" alt="Innoclique" width="163" height="36"></a>
  <div class="links">
    <a href="#products">Products</a>
    <a href="#compare">Compare</a>
    <a href="#convert">Plan to 3D</a>
    <a href="#deliverables">Deliverables</a>
    <a class="btn" href="#contact">Send us a scan</a>
  </div>
</nav></div></header>

<main id="top">
<div class="hero">
  <canvas id="cloud"></canvas>
  <div class="wrap">
    <h1>Catch every <em>mismatch</em> between CAD and Revit.</h1>
    <p>{escape(SITE['intro'])}</p>
    <div class="cta">
      <a class="btn alt" href="#compare">Compare drawings</a>
      <a class="btn ghost" href="#convert">Plan to 3D</a>
    </div>
    <div class="flow">Upload &rarr; Compare &rarr; Fix</div>
  </div>
</div>

{CMP_HTML}

{TOOL_HTML}

<section id="products"><div class="wrap">
  <div class="eyebrow">Products</div><h2>Built on Innoclique.</h2>
  <p class="sub">Upload a scan, get a model you can check against it.</p>
  <div class="grid">{product_cards()}</div>
</div></section>

<section id="deliverables"><div class="wrap">
  <div class="eyebrow">Deliverables</div>
  <h2>Everything we return from one scan.</h2>
  <p class="sub">Scan to BIM is one thing we do. Most of what comes back from a
  scan is not a model at all. It is the counts, plans, measurements and answers
  your team would otherwise pull out of the point cloud by hand.</p>

  <h3 style="margin-bottom:6px">The files</h3>
  <p class="sub" style="margin-bottom:18px">Each deliverable arrives in the format
  the people who use it already work in. Nothing needs our software to open.</p>
  <div class="tbl-wrap"><table>
    <thead><tr><th>What you get</th><th>Delivered as</th><th>Who usually asks for it</th></tr></thead>
    <tbody>{deliverable_rows()}</tbody>
  </table></div>

  <div class="two">
    <div class="card"><h3>The viewer</h3>
      <p class="muted">Every scan also comes back hosted in a viewer where each
      element is labeled and pinned where it sits. Ask it a question in plain
      language and the answer lights up in the point cloud. There is no menu of
      reports. If you need a count that is not on the list, you type it.</p></div>
    <div class="card"><h3>What we need from you</h3>
      <p class="muted">One scan you already have, as <code>E57</code>,
      <code>LAS</code> or <code>LAZ</code>. Tell us what was captured and what you
      want back. We will show you the result and quote the job. A model is
      usually back within an hour.</p></div>
    <div class="card"><h3>Every number is measured</h3>
      <p class="muted">Nothing on a sheet is estimated from a photo or typed in
      by a person. Each count, length and area is measured from the points in the
      scan, and each element records how much of it the scanner actually saw, so
      you know which numbers to trust and which to check.</p></div>
  </div>
  <p style="margin-top:32px"><a class="btn" href="#contact">Send us a scan</a></p>
</div></section>

<section id="contact" class="contact"><div class="wrap">
  <div class="eyebrow">Work with us</div>
  <h2>Send us a scan. We will show you what we were able to return.</h2>
  <p class="sub">Or ask for a quote for API or end-user access. Tell us what you
  scan and how often, and we will price it to match.</p>
  <form onsubmit="sendScan(event)">
    <input name="name" placeholder="Your name" required>
    <input name="email" type="email" placeholder="Your email" required>
    <select name="topic">
      <option>Send us a scan</option><option>Ask for a quote</option>
    </select>
    <textarea name="msg" rows="4" placeholder="What do you scan, and how often?"></textarea>
    <button class="btn" type="submit">Open email</button>
  </form>
</div></section>
</main>

<footer><div class="wrap">
  <div class="fgrid">
    <div><img src="{LOGO}" alt="Innoclique" height="32" style="height:32px;width:auto;margin-bottom:12px">
      <p>We turn scans into BIM models, counts, measurements, and answers for
      anyone who needs to know what is in a space.</p></div>
    <div><h4>Company</h4><a href="#products">Products</a>
      <a href="#deliverables">Deliverables</a></div>
    <div><h4>Contact</h4><a href="#contact">Send us a scan</a>
      <a href="#contact">Ask for a quote</a></div>
  </div>
  <p>&copy; 2026 {SITE['name']}</p>
</div></footer>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script src="https://cdn.jsdelivr.net/npm/pdfjs-dist@3.11.174/build/pdf.min.js"></script>
<script>{JS}</script>
<script>{TOOL_JS}</script>
<script>{CMP_JS}</script>
</body></html>"""


# ----------------------------- RUN ----------------------------------------
def main():
    out = Path(__file__).with_name("index.html")
    out.write_text(build_html(), encoding="utf-8")
    print(f"Wrote {out}")

    handler = lambda *a, **k: http.server.SimpleHTTPRequestHandler(
        *a, directory=str(out.parent), **k)
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), handler) as srv:
        url = f"http://localhost:{PORT}"
        print(f"Serving at {url}  (Ctrl+C to stop)")
        webbrowser.open(url)
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")


if __name__ == "__main__":
    main()