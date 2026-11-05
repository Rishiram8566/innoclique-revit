"""
Innoclique - landing page generator + local server.
Pure Python standard library: no pip installs, no hosting cost.

Run:   python innoclique_site.py
Open:  http://localhost:8000
Also writes a static index.html you can upload to any free host
(GitHub Pages, Netlify, Cloudflare Pages).
"""
import http.server
import socketserver
import webbrowser
from html import escape
from pathlib import Path

PORT = 8000

# Innoclique logo (taken from the Smart Receiving prototype), embedded as data URI
LOGO = "data:image/webp;base64,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"

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
window.IQ={otsu,dilate,ccl};
function status(t,e){const s=$('status');s.textContent=t;s.style.color=e?'#e5484d':'';}
if(!window.THREE){status('3D library failed to load. Check your internet connection.',true);return;}
const hgt=()=>parseFloat($('wh').value);

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
  const inv=$('inv').checked,f=Math.max(1,Math.ceil(Math.max(w,h)/480)),W=Math.ceil(w/f),H=Math.ceil(h/f);
  const g=new Uint8Array(W*H).fill(255);
  for(let y=0;y<h;y++){const row=((y/f)|0)*W;for(let x=0;x<w;x++){const i=(y*w+x)*4;
    let v=(d[i]*.3+d[i+1]*.59+d[i+2]*.11)|0;if(inv)v=255-v;const k=row+((x/f)|0);if(v<g[k])g[k]=v;}}
  if(first||S.reth){const hs=new Array(256).fill(0);for(let i=0;i<g.length;i++)hs[g[i]]++;
    const t=Math.min(250,otsu(hs,W*H)+1);$('thr').value=t;$('o_thr').textContent=t;}
  S.fresh=S.reth=false;
  const thr=+$('thr').value;let m=new Uint8Array(W*H);
  for(let i=0;i<m.length;i++)m[i]=g[i]<thr?1:0;
  m=dilate(m,W,H,+$('thick').value);
  const sp=+$('speck').value;
  if(sp>0){const L=ccl(m,W,H,1);for(let i=0;i<m.length;i++)if(m[i]&&L.sizes[L.lab[i]]<sp)m[i]=0;}
  dyn.forEach(o=>{scene.remove(o);if(o.geometry)o.geometry.dispose();});dyn=[];S.pins=[];
  const rects=rectsOf(m,W,H);
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
  S.rooms=rooms;
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
  const st=[['Rooms',rooms.length],['Room area',rooms.reduce((a,r)=>a+r.area,0).toFixed(1)+' m2'],
    ['Footprint',((x1-x0)*c).toFixed(1)+' x '+((y1-y0)*c).toFixed(1)+' m'],
    ['Wall length (approx)',(wa/th*c).toFixed(1)+' m'],['Wall area (plan)',(wa*c*c).toFixed(1)+' m2'],
    ['Wall volume',(wa*c*c*hgt()).toFixed(1)+' m3'],['Wall blocks',rects.length]];
  $('stats').innerHTML=st.map(a=>'<div class="card"><div class="muted">'+a[0]+'</div><h3>'+a[1]+'</h3></div>').join('');
  $('rooms').innerHTML=rooms.length?rooms.map((r,i)=>'<tr class="rr" data-i="'+i+'"><td>Room '+(i+1)+'</td><td>'+r.area.toFixed(1)+' m2</td><td>'+r.w.toFixed(1)+' x '+r.d.toFixed(1)+' m</td></tr>').join(''):
    '<tr><td colspan="3" class="muted">No closed rooms found. Increase "Close doorways".</td></tr>';
  status('Done: '+rooms.length+' rooms, '+rects.length+' wall blocks. Drag to orbit, scroll to zoom.');
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
  return '# Innoclique plan to 3D\n'+v.join('\n')+'\n'+f.join('\n')+'\n';}

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
  pick, and highlights each mismatch. It runs in your browser and nothing is uploaded.</p>
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
        <span><i style="background:#94a3b8"></i>Matching</span><span>Scroll to zoom, drag to pan</span></div>
      <div class="vp" id="vp"><div class="lay" id="lay"><canvas id="ov"></canvas><div id="mks"></div></div></div>
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
const $=id=>document.getElementById(id),{otsu,ccl}=window.IQ;
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
function fit(){z=Math.min(vp.clientWidth/C.W,vp.clientHeight/C.H);tx=(vp.clientWidth-C.W*z)/2;ty=(vp.clientHeight-C.H*z)/2;view();}
vp.addEventListener('wheel',e=>{e.preventDefault();const r=vp.getBoundingClientRect(),mx=e.clientX-r.left,my=e.clientY-r.top,k=e.deltaY<0?1.15:1/1.15;tx=mx-(mx-tx)*k;ty=my-(my-ty)*k;z*=k;view();},{passive:false});
let dr=null;vp.addEventListener('pointerdown',e=>{dr=[e.clientX-tx,e.clientY-ty];vp.setPointerCapture(e.pointerId);vp.style.cursor='grabbing';});
vp.addEventListener('pointermove',e=>{if(dr){tx=e.clientX-dr[0];ty=e.clientY-dr[1];view();}});
vp.addEventListener('pointerup',()=>{dr=null;vp.style.cursor='grab';});
function focus(i){const s=C.res.issues[i];z=Math.min(vp.clientWidth,vp.clientHeight)/Math.max(s.gr*6,160);tx=vp.clientWidth/2-s.gx*z;ty=vp.clientHeight/2-s.gy*z;view();}

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
  status('Compared. '+r.issues.length+' issue(s) found. Click a row to zoom to it.');fit();}

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