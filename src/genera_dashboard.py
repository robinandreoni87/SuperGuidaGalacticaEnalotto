import os
import re
import json
import math

# Configurazione percorsi
input_dir = r"C:\Users\robin\Desktop\super"
output_html = os.path.join(input_dir, "dashboard_statistica.html")

def nCr(n, r):
    if r < 0 or r > n: return 0
    if r == 0 or r == n: return 1
    if r > n // 2: r = n - r
    return math.comb(n, r)

def get_sestina_index(comb):
    comb = sorted(comb)
    index = 0
    current_val = 1
    for i in range(6):
        for v in range(current_val, comb[i]):
            index += nCr(90 - v, 6 - (i + 1))
        current_val = comb[i] + 1
    return index

def parse_files():
    all_draws = []
    files = [f for f in os.listdir(input_dir) if f.startswith("estrazioni") and f.endswith(".txt")]
    files.sort(reverse=True)
    pattern = re.compile(r"N.*?(\d+)\s+-\s+Concorso del (.*?)\r?\nNumeri:\s+(.*?)\r?\nJolly:\s+(\d+)\r?\nSuperStar:\s*(\d*)", re.IGNORECASE)

    for file in files:
        path = os.path.join(input_dir, file)
        anno_raw = file.replace("estrazioni", "").replace(".txt", "").strip("_")
        anno_file = "2026" if "pulite" in anno_raw or "2026" in anno_raw else anno_raw
        if not anno_file.isdigit(): continue
            
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                matches = pattern.findall(content)
                for m in matches:
                    nums = [int(n) for n in m[2].split()]
                    all_draws.append({
                        "concorso": m[0], "data": m[1].strip(), "numeri": nums,
                        "jolly": int(m[3]) if m[3] else 0, "superstar": int(m[4]) if m[4] else 0,
                        "anno": anno_file, "index": get_sestina_index(nums), "sum": sum(nums)
                    })
        except Exception as e: print(f"Errore {file}: {e}")
    return all_draws[::-1]

def calculate_stats(draws):
    global_stats = {n: {"freq": 0, "delay": 0} for n in range(1, 91)}
    years_data = {}
    all_years = sorted(list(set(d["anno"] for d in draws)), reverse=True)
    map_points = []
    total_possibilities = 622614630; canvas_w = 1000; canvas_h = 600

    for i, draw in enumerate(draws):
        yr = draw["anno"]
        if yr not in years_data: years_data[yr] = {"freq": {n: 0 for n in range(1, 91)}, "count": 0}
        years_data[yr]["count"] += 1
        idx = draw["index"]
        x1 = (idx % canvas_w); y1 = int(idx / (total_possibilities / canvas_h))
        x2 = x1; y2 = int(((draw["sum"] - 21) / 504) * canvas_h)
        map_points.append({"x1": x1, "y1": y1, "x2": x2, "y2": y2, "idx": idx, "sum": draw["sum"], "c": draw["concorso"], "a": draw["anno"], "n": draw["numeri"]})
        for n in draw["numeri"]: global_stats[n]["freq"] += 1; years_data[yr]["freq"][n] += 1

    draws_desc = draws[::-1]; found = set()
    for i, d in enumerate(draws_desc):
        for n in d["numeri"]:
            if n not in found: global_stats[n]["delay"] = i; found.add(n)

    return {
        "total_draws": len(draws), "years": all_years, "global_stats": global_stats, "years_data": years_data,
        "coverage": round((len(draws) / total_possibilities) * 100, 8), "map_points": map_points
    }

def generate_html(data):
    json_data = json.dumps(data)
    html_template = f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SuperEnalotto - Extreme Analytics 5.7</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{ --bg: #0b0f19; --card: #151c2c; --accent: #38bdf8; --text: #f8fafc; --text-dim: #94a3b8; --fut: #a855f7; --danger: #ef4444; }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); padding: 15px; padding-bottom: 80px; overflow-x: hidden; }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        
        header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; border-bottom: 1px solid #2d3748; padding-bottom: 1rem; flex-wrap: wrap; gap: 15px; }}
        .logo {{ font-size: 1.4rem; font-weight: 700; color: var(--accent); }}
        .controls {{ display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }}
        
        .btn {{ background: var(--card); color: var(--accent); border: 1px solid var(--accent); padding: 8px 12px; border-radius: 8px; font-weight: 600; cursor: pointer; font-size: 0.75rem; transition: 0.2s; }}
        .btn:hover, .btn.active {{ background: var(--accent); color: #000; }}
        .btn-fut {{ border-color: var(--fut); color: var(--fut); }}
        .btn-fut:hover, .btn-fut.active {{ background: var(--fut); color: #fff; }}
        .btn-danger {{ border-color: var(--danger); color: var(--danger); font-weight: 800; }}
        .btn-danger:hover {{ background: var(--danger); color: #fff; }}
        
        .map-wrapper {{ display: none; margin-top: 1rem; margin-bottom: 3rem; border: 1px solid var(--accent); padding: 25px; border-radius: 1.2rem; background: #000; flex-direction: column; align-items: center; position: relative; width: 100%; }}
        canvas {{ background: #000; border: 1px solid rgba(56, 189, 248, 0.2); border-radius: 6px; display: block; max-width: 100%; height: auto !important; }}
        
        #player-controls {{ display: flex; align-items: center; gap: 15px; margin-bottom: 15px; background: rgba(56, 189, 248, 0.1); padding: 10px 20px; border-radius: 50px; border: 1px solid rgba(56, 189, 248, 0.2); flex-wrap: wrap; justify-content: center; }}
        input[type=range] {{ width: 250px; cursor: pointer; accent-color: var(--accent); }}
        #timer, #evTimer, #futTimer {{ font-family: monospace; color: var(--accent); font-size: 0.95rem; min-width: 120px; text-align: center; font-weight: 700; }}
        
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 1.5rem; }}
        .card {{ background: var(--card); border-radius: 1rem; padding: 1.5rem; border: 1px solid #2d3748; }}
        .card-title {{ font-size: 0.9rem; font-weight: 600; margin-bottom: 1.2rem; border-left: 3px solid var(--accent); padding-left: 10px; color: var(--text-dim); text-transform: uppercase; }}
        
        .ball {{ width: 26px; height: 26px; background: #2d3748; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.75rem; }}
        .ball.active {{ background: var(--accent); color: #000; }}
        
        #future-panel {{ position: absolute; right: 20px; top: 120px; width: 200px; height: 460px; background: rgba(0,0,0,0.85); border: 1px solid var(--fut); border-radius: 12px; padding: 10px; overflow-y: auto; display: none; color: var(--fut); font-family: monospace; font-size: 0.7rem; }}
        .fut-row {{ border-bottom: 1px solid rgba(168,85,247,0.2); padding: 8px 0; }}
        #tooltip {{ position: absolute; background: rgba(11, 15, 25, 0.98); border: 1px solid var(--accent); padding: 12px; border-radius: 8px; display: none; pointer-events: none; z-index: 1000; }}

        #loading-overlay {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 10000; display: none; flex-direction: column; align-items: center; justify-content: center; }}
        .loader {{ border: 4px solid #f3f3f3; border-top: 4px solid var(--accent); border-radius: 50%; width: 50px; height: 50px; animation: spin 1s linear infinite; }}
        @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}

        @media (max-width: 768px) {{
            header {{ flex-direction: column; text-align: center; }}
            .controls {{ justify-content: center; }}
            .grid {{ grid-template-columns: 1fr; }}
            #future-panel {{ position: relative; top: 0; right: 0; width: 100%; height: 200px; margin-top: 15px; }}
        }}
    </style>
</head>
<body>
    <div id="loading-overlay"><div class="loader"></div><div id="loading-text" style="margin-top:20px; font-weight:700">Elaborazione 150.000 combinazioni...</div></div>
    <div id="tooltip"></div>
    <div class="container">
        <header>
            <div class="logo">SuperEnalotto Analytics</div>
            <div class="controls">
                <select id="yearSelect" onchange="updateDashboard()" style="background:var(--card);color:white;border:1px solid var(--accent);padding:8px;border-radius:8px;font-weight:700">
                    <option value="ALL">TUTTI GLI ANNI</option>
                    {"".join([f'<option value="{y}">{y}</option>' for y in data['years']])}
                </select>
                <button class="btn" id="btn_dict" onclick="toggleMap('dict')">MAPPA DIZIONARIO</button>
                <button class="btn" id="btn_stat" onclick="toggleMap('stat')">MAPPA STATISTICA</button>
                <button class="btn" id="btn_fusion" onclick="toggleMap('fusion')">FUSIONE MAPPE</button>
                <button class="btn" id="btn_evolution" onclick="toggleMap('evolution')">EVOLUZIONE STORICA</button>
                <button class="btn btn-fut" id="btn_future" onclick="toggleMap('future')">SIMULAZIONE FUTURISTICA</button>
            </div>
        </header>

        <div id="mapSection" class="map-wrapper"><div class="card-title" id="mapTitle" style="color:white">Mappa</div><canvas id="mapCanvas" width="1000" height="600"></canvas></div>

        <div id="fusionSection" class="map-wrapper">
            <div id="player-controls"><button class="btn" id="playPauseBtn" onclick="togglePause()">PAUSE</button><input type="range" id="progressSlider" min="0" max="100" value="0" oninput="manualControl(this.value)"><div id="timer">60s</div></div>
            <div style="display:flex; gap:20px; width:100%; justify-content:center; flex-wrap:wrap"><canvas id="canvasLeft" width="600" height="600"></canvas><canvas id="canvasRight" width="600" height="600"></canvas></div>
        </div>

        <div id="evolutionSection" class="map-wrapper">
            <div id="player-controls"><button class="btn" id="evPlayPauseBtn" onclick="togglePauseEv()">PAUSE</button><input type="range" id="evSlider" min="0" max="{data['total_draws']-1}" value="0" oninput="manualControlEv(this.value)"><div id="evTimer">1997</div></div>
            <canvas id="canvasEv" width="1000" height="600"></canvas>
        </div>

        <div id="futureSection" class="map-wrapper" style="border-color:var(--fut)">
            <div id="player-controls" style="background:rgba(168,85,247,0.1); border-color:rgba(168,85,247,0.2)">
                <button class="btn" style="border-color:var(--fut); color:var(--fut)" id="futPlayBtn" onclick="togglePauseFut()">PAUSE</button>
                <input type="range" id="futSlider" min="0" max="150000" value="0" oninput="manualControlFut(this.value)" style="accent-color:var(--fut)">
                <div id="futTimer" style="color:var(--fut)">SIMULAZIONE: 0</div>
                <button class="btn" style="border-color:var(--fut); background:var(--fut); color:#fff" onclick="exportFuture()">SALVA</button>
                <button class="btn" style="border-color:var(--fut); border-style:dashed; color:var(--fut)" onclick="document.getElementById('fileInput').click()">CARICA EXTREME</button>
                <button class="btn btn-danger" onclick="alert('Esegui prima lo script massive_gauss_gen.py e poi carica il file gauss_complete_80_EXTREME.md')">COMPLETA GAUSS (150k)</button>
                <input type="file" id="fileInput" style="display:none" onchange="importFuture(event)">
            </div>
            <div id="future-panel"></div>
            <canvas id="canvasFut" width="1000" height="600"></canvas>
        </div>

        <div id="dashboardStats" class="grid">
            <div class="card" style="grid-column: span 2;"><div class="card-title">Distribuzione Frequenza</div><canvas id="freqChart"></canvas></div>
            <div class="card"><div class="card-title">Ritardatari (Globale)</div><ul id="delayedList" style="list-style:none"></ul></div>
            <div class="card"><div class="card-title" id="hotTitle">Hot Numbers</div><ul id="hotList" style="list-style:none"></ul></div>
            <div class="card"><div class="card-title" id="coldTitle">Cold Numbers</div><ul id="coldList" style="list-style:none"></ul></div>
        </div>
    </div>

    <script>
        const rawData = {json_data};
        let currentMode = '', isPaused = false, animationId = null, startTime = 0, elapsedAtPause = 0, currentProgress = 1;
        let isEvPaused = false, evAnimationId = null, currentIdx = 0;
        let isFutPaused = false, futAnimationId = null, futPoints = [];
        let freqChart = null;

        function toggleMap(mode) {{
            const sections = ['mapSection', 'fusionSection', 'evolutionSection', 'futureSection'];
            sections.forEach(s => document.getElementById(s).style.display = 'none');
            document.getElementById('dashboardStats').style.display = (mode === '') ? 'grid' : 'none';
            document.getElementById('future-panel').style.display = (mode === 'future') ? 'block' : 'none';
            if(animationId) cancelAnimationFrame(animationId);
            if(evAnimationId) clearInterval(evAnimationId);
            if(futAnimationId) cancelAnimationFrame(futAnimationId);
            if (currentMode === mode) {{ currentMode = ''; document.getElementById('dashboardStats').style.display = 'grid'; updateDashboard(); }} 
            else {{ currentMode = mode; let targetId = (mode === 'dict' || mode === 'stat') ? 'mapSection' : mode + 'Section';
                document.getElementById(targetId).style.display = 'flex';
                if(mode === 'fusion') resetFusion();
                else if(mode === 'evolution') resetEvolution();
                else if(mode === 'future') resetFuture();
                else {{ currentProgress = 1; drawStaticMap(); }}
            }}
            updateButtonState();
        }}

        function updateButtonState() {{ ['dict','stat','fusion','evolution','future'].forEach(m => {{ const btn = document.getElementById('btn_' + m); if(btn) btn.classList.toggle('active', currentMode === m); }}); }}

        function drawStaticMap() {{
            const canvas = document.getElementById('mapCanvas'); const ctx = canvas.getContext('2d');
            ctx.clearRect(0,0,1000,600); rawData.map_points.forEach(p => {{ ctx.fillStyle = '#38bdf8'; ctx.fillRect(p.x1, currentMode === 'dict' ? p.y1 : p.y2, 3, 3); }});
            canvas.onmousemove = e => handleHover(e, canvas, currentMode, rawData.map_points.length);
        }}

        function resetFusion() {{ isPaused = false; startTime = Date.now(); animateFusion(); }}
        function togglePause() {{ isPaused = !isPaused; if(isPaused) {{ elapsedAtPause = Date.now()-startTime; cancelAnimationFrame(animationId); }} else {{ startTime = Date.now()-elapsedAtPause; animateFusion(); }} document.getElementById('playPauseBtn').innerText = isPaused?'PLAY':'PAUSE'; }}
        function manualControl(val) {{ if(!isPaused) togglePause(); currentProgress = val/100; elapsedAtPause = currentProgress * 60000; drawFusionFrame(currentProgress); }}
        function animateFusion() {{
            const elapsed = Date.now() - startTime; currentProgress = Math.min(elapsed / 60000, 1);
            document.getElementById('progressSlider').value = currentProgress * 100;
            document.getElementById('timer').innerText = Math.ceil((60000 - (currentProgress*60000))/1000) + 's';
            drawFusionFrame(currentProgress); if(currentProgress < 1 && !isPaused) animationId = requestAnimationFrame(animateFusion);
        }}
        function drawFusionFrame(progress) {{
            const cL = document.getElementById('canvasLeft'); const cR = document.getElementById('canvasRight');
            const ctxL = cL.getContext('2d'); const ctxR = cR.getContext('2d');
            ctxL.clearRect(0,0,600,600); ctxR.clearRect(0,0,600,600);
            const limit = Math.floor(progress * rawData.map_points.length); ctxL.fillStyle = ctxR.fillStyle = '#38bdf8';
            for(let i=0; i<limit; i++) {{ const p = rawData.map_points[i]; ctxL.fillRect((p.x1/1000)*600, p.y1, 2, 2); ctxR.fillRect((p.x1/1000)*600, p.y2, 2, 2); }}
            cL.onmousemove = e => handleHover(e, cL, 'dict_fusion', limit); cR.onmousemove = e => handleHover(e, cR, 'stat_fusion', limit);
        }}

        function resetEvolution() {{ currentIdx = 0; isEvPaused = false; clearInterval(evAnimationId); evAnimationId = setInterval(() => {{ if(currentIdx < rawData.map_points.length) {{ drawEvolutionFrame(currentIdx); currentIdx++; }} }}, 1000); }}
        function togglePauseEv() {{ isEvPaused = !isEvPaused; if(isEvPaused) clearInterval(evAnimationId); else evAnimationId = setInterval(() => {{ if(currentIdx < rawData.map_points.length) {{ drawEvolutionFrame(currentIdx); currentIdx++; }} }}, 1000); document.getElementById('evPlayPauseBtn').innerText = isEvPaused?'PLAY':'PAUSE'; }}
        function manualControlEv(val) {{ currentIdx = parseInt(val); if(!isEvPaused) togglePauseEv(); drawEvolutionFrame(currentIdx); }}
        function drawEvolutionFrame(idx) {{
            const canvas = document.getElementById('canvasEv'); const ctx = canvas.getContext('2d');
            ctx.clearRect(0,0,1000,600); ctx.fillStyle = '#38bdf8';
            for(let i=0; i<=idx; i++) ctx.fillRect(rawData.map_points[i].x1, rawData.map_points[i].y2, 3, 3);
            const p = rawData.map_points[idx]; document.getElementById('evSlider').value = idx;
            document.getElementById('evTimer').innerText = p.a + ' | N.' + p.c; canvas.onmousemove = e => handleHover(e, canvas, 'stat', idx+1);
        }}

        function resetFuture() {{ futPoints = []; isFutPaused = false; document.getElementById('future-panel').innerHTML = ''; animateFuture(); }}
        function togglePauseFut() {{ isFutPaused = !isFutPaused; if(!isFutPaused) animateFuture(); document.getElementById('futPlayBtn').innerText = isFutPaused?'PLAY':'PAUSE'; }}
        function manualControlFut(val) {{ if(!isFutPaused) togglePauseFut(); const target = parseInt(val); while(futPoints.length < target) generateFutPoint(); while(futPoints.length > target) futPoints.pop(); renderFuture(); }}
        
        function generateFutPoint() {{
            const u1 = Math.random(), u2 = Math.random();
            const z0 = Math.sqrt(-2.0 * Math.log(u1)) * Math.cos(2.0 * Math.PI * u2);
            const sum = 273 + (z0 * 42);
            const nums = []; while(nums.length<6) {{ const n=1+Math.floor(Math.random()*90); if(!nums.includes(n)) nums.push(n); }}
            nums.sort((a,b)=>a-b); const idx = Math.floor(Math.random()*622614630);
            const p = {{x: idx%1000, y: Math.max(0, Math.min(600, ((sum-21)/504)*600)), n: nums, s: Math.round(sum)}};
            futPoints.push(p);
            if(futPoints.length < 500 && futPoints.length % 50 === 0) {{
                const panel = document.getElementById('future-panel');
                panel.innerHTML = `<div class="fut-row">Sestina: ${{p.n.join(' ')}}\\nSomma: ${{p.s}}</div>` + panel.innerHTML;
            }}
        }}
        function animateFuture() {{ if(isFutPaused) return; for(let i=0; i<200; i++) if(futPoints.length < 150000) generateFutPoint(); renderFuture(); if(futPoints.length < 150000) futAnimationId = requestAnimationFrame(animateFuture); }}
        function renderFuture() {{
            const canvas = document.getElementById('canvasFut'); const ctx = canvas.getContext('2d');
            ctx.clearRect(0,0,1000,600); ctx.fillStyle = 'rgba(168,85,247,0.15)'; ctx.fillRect(0, ((250-21)/504)*600, 1000, ((300-250)/504)*600);
            ctx.fillStyle = '#38bdf8'; rawData.map_points.forEach(p => ctx.fillRect(p.x1, p.y2, 2, 2));
            ctx.fillStyle = 'var(--fut)'; 
            // Rendering efficiente
            futPoints.forEach(p => ctx.fillRect(p.x, p.y, 1, 1));
            document.getElementById('futTimer').innerText = 'SIMULAZIONE: +' + futPoints.length;
            document.getElementById('futSlider').value = futPoints.length;
        }}

        function exportFuture() {{
            let content = "# EXPORT SIMULAZIONE EXTREME\\n# Totale: " + futPoints.length + " combinazioni\\n\\n";
            futPoints.forEach(p => {{ content += "Sestina: " + p.n.join(' ') + "\\nSomma: " + p.s + "\\n\\n"; }});
            const blob = new Blob([content], {{type: 'text/markdown'}});
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a'); a.href = url; a.download = 'gauss_extreme_' + Date.now() + '.md'; a.click();
        }}

        function importFuture(event) {{
            const file = event.target.files[0]; if(!file) return;
            document.getElementById('loading-overlay').style.display = 'flex';
            const reader = new FileReader();
            reader.onload = function(e) {{
                const text = e.target.result;
                const lines = text.split('\\n');
                futPoints = [];
                let currentSestina = null;
                for(let line of lines) {{
                    if(line.startsWith('Sestina:')) currentSestina = line.replace('Sestina:', '').trim().split(' ').map(Number);
                    else if(line.startsWith('Somma:') && currentSestina) {{
                        const somma = parseInt(line.replace('Somma:', '').trim());
                        const idx = Math.floor(Math.random()*622614630);
                        futPoints.push({{x: idx%1000, y: Math.max(0, Math.min(600, ((somma-21)/504)*600)), n: currentSestina, s: somma}});
                        currentSestina = null;
                    }}
                }}
                document.getElementById('loading-overlay').style.display = 'none';
                renderFuture();
                alert('Caricate ' + futPoints.length + ' combinazioni nel motore grafico!');
            }};
            reader.readAsText(file);
        }}

        function handleHover(e, canvas, mode, limit) {{
            const rect = canvas.getBoundingClientRect(); const mx = (e.clientX-rect.left) * (canvas.width / rect.width); const my = (e.clientY-rect.top) * (canvas.height / rect.height);
            const tool = document.getElementById('tooltip'); let found = null;
            const points = (mode==='dict' || mode==='stat') ? rawData.map_points : (mode==='dict_fusion' || mode==='stat_fusion' ? rawData.map_points : []);
            if(points.length === 0) return;
            for(let i=0; i<limit; i++) {{
                const p = points[i]; let px, py;
                if(mode==='dict') {{px=p.x1; py=p.y1;}} else if(mode==='stat') {{px=p.x1; py=p.y2;}}
                else if(mode==='dict_fusion') {{px=(p.x1/1000)*600; py=p.y1;}} else if(mode==='stat_fusion') {{px=(p.x1/1000)*600; py=p.y2;}}
                if(Math.abs(px-mx)<5 && Math.abs(py-my)<5) {{ found=p; break; }}
            }}
            if (found) {{
                tool.style.display='block'; tool.style.left=(e.pageX+15)+'px'; tool.style.top=(e.pageY+15)+'px';
                tool.innerHTML = `<div style="color:var(--accent);font-weight:700">CONCORSO ${{found.c}}</div>
                    <div style="display:flex;gap:4px;margin:5px 0">${{found.n.map(n=>`<span class="ball active" style="width:20px;height:20px;font-size:0.65rem">${{n}}</span>`).join('')}}</div>
                    <div style="color:var(--text-dim);font-size:0.6rem">Somma: ${{found.sum}}</div>`;
            }} else tool.style.display='none';
        }}

        function updateDashboard() {{
            const yr = document.getElementById('yearSelect').value;
            let stats = {{}}; if(yr==='ALL') {{ for(let n=1; n<=90; n++) stats[n]=rawData.global_stats[n].freq; }} else stats=rawData.years_data[yr].freq;
            const sorted = Object.entries(stats).sort((a,b)=>b[1]-a[1]);
            const ctxF = document.getElementById('freqChart');
            if(freqChart && typeof freqChart.destroy === 'function') {{ freqChart.destroy(); }}
            freqChart = new Chart(ctxF, {{ type: 'bar', data: {{ labels: sorted.slice(0,15).map(x=>'N.'+x[0]), datasets: [{{ label: 'Freq', data: sorted.slice(0,15).map(x=>x[1]), backgroundColor: '#38bdf8' }}] }}, options: {{ plugins: {{ legend:{{display:false}} }}, scales: {{ y: {{ grid: {{color:'#2d3748'}} }} }} }} }});
            document.getElementById('hotList').innerHTML = ''; sorted.slice(0,10).forEach(x=> document.getElementById('hotList').innerHTML += `<li style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid #2d3748"><span><span class="ball active">${{x[0]}}</span></span> <span>${{x[1]}}</span></li>`);
            document.getElementById('coldList').innerHTML = ''; sorted.slice(-10).reverse().forEach(x=> document.getElementById('coldList').innerHTML += `<li style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid #2d3748"><span><span class="ball">${{x[0]}}</span></span> <span>${{x[1]}}</span></li>`);
            const delEl = document.getElementById('delayedList'); delEl.innerHTML = '';
            if(yr==='ALL') {{ Object.entries(rawData.global_stats).sort((a,b)=>b[1].delay-a[1].delay).slice(0,10).forEach(x=> delEl.innerHTML += `<li style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid #2d3748"><span><span class="ball active">${{x[0]}}</span></span> <span>${{x[1].delay}}</span></li>`); }}
        }}
        updateDashboard();
    </script>
</body>
</html>
"""
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html_template)

if __name__ == "__main__":
    print("Analisi file in corso...")
    draws = parse_files()
    if not draws: print("ERRORE!")
    else:
        stats = calculate_stats(draws)
        generate_html(stats)
        print(f"Dashboard 5.7 EXTREME Pronta: {output_html}")
