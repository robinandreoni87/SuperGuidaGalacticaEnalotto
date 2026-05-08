let currentMode = '', isPaused = false, animationId = null, startTime = 0, elapsedAtPause = 0, currentProgress = 1;
let isEvPaused = false, evAnimationId = null, currentIdx = 0;
let isFutPaused = false, futAnimationId = null, futPoints = [];
let freqChart = null;

// Inizializzazione Dropdown Anni
function initYearSelect() {
    const select = document.getElementById('yearSelect');
    let html = '<option value="ALL">TUTTI GLI ANNI</option>';
    rawData.years.forEach(y => { html += `<option value="${y}">${y}</option>`; });
    select.innerHTML = html;
    
    // Inizializza slider evoluzione
    document.getElementById('evSlider').max = rawData.map_points.length - 1;
}

function toggleMap(mode) {
    const sections = ['mapSection', 'fusionSection', 'evolutionSection', 'futureSection'];
    sections.forEach(s => document.getElementById(s).style.display = 'none');
    document.getElementById('dashboardStats').style.display = (mode === '') ? 'grid' : 'none';
    document.getElementById('future-panel').style.display = (mode === 'future') ? 'block' : 'none';
    
    if(animationId) cancelAnimationFrame(animationId);
    if(evAnimationId) clearInterval(evAnimationId);
    if(futAnimationId) cancelAnimationFrame(futAnimationId);

    if (currentMode === mode) {
        currentMode = '';
        document.getElementById('dashboardStats').style.display = 'grid';
        updateDashboard();
    } else {
        currentMode = mode;
        let targetId = (mode === 'dict' || mode === 'stat') ? 'mapSection' : mode + 'Section';
        document.getElementById(targetId).style.display = 'flex';
        if(mode === 'fusion') resetFusion();
        else if(mode === 'evolution') resetEvolution();
        else if(mode === 'future') resetFuture();
        else { currentProgress = 1; drawStaticMap(); }
    }
    updateButtonState();
}

function updateButtonState() {
    ['dict','stat','fusion','evolution','future'].forEach(m => {
        const btn = document.getElementById('btn_' + m);
        if(btn) btn.classList.toggle('active', currentMode === m);
    });
}

function drawStaticMap() {
    const canvas = document.getElementById('mapCanvas'); const ctx = canvas.getContext('2d');
    ctx.clearRect(0,0,1000,600);
    document.getElementById('mapTitle').innerText = currentMode === 'dict' ? 'Mappa Dizionario' : 'Mappa Statistica';
    rawData.map_points.forEach(p => { ctx.fillStyle = '#38bdf8'; ctx.fillRect(p.x1, currentMode === 'dict' ? p.y1 : p.y2, 3, 3); });
    canvas.onmousemove = e => handleHover(e, canvas, currentMode, rawData.map_points.length);
}

function resetFusion() { isPaused = false; startTime = Date.now(); animateFusion(); }
function togglePause() { 
    isPaused = !isPaused; 
    if(isPaused) { elapsedAtPause = Date.now()-startTime; cancelAnimationFrame(animationId); }
    else { startTime = Date.now()-elapsedAtPause; animateFusion(); }
    document.getElementById('playPauseBtn').innerText = isPaused?'PLAY':'PAUSE';
}
function manualControl(val) { if(!isPaused) togglePause(); currentProgress = val/100; elapsedAtPause = currentProgress * 60000; drawFusionFrame(currentProgress); }
function animateFusion() {
    const elapsed = Date.now() - startTime; currentProgress = Math.min(elapsed / 60000, 1);
    document.getElementById('progressSlider').value = currentProgress * 100;
    document.getElementById('timer').innerText = Math.ceil((60000 - (currentProgress*60000))/1000) + 's';
    drawFusionFrame(currentProgress); if(currentProgress < 1 && !isPaused) animationId = requestAnimationFrame(animateFusion);
}
function drawFusionFrame(progress) {
    const cL = document.getElementById('canvasLeft'); const cR = document.getElementById('canvasRight');
    const ctxL = cL.getContext('2d'); const ctxR = cR.getContext('2d');
    ctxL.clearRect(0,0,600,600); ctxR.clearRect(0,0,600,600);
    const limit = Math.floor(progress * rawData.map_points.length); ctxL.fillStyle = ctxR.fillStyle = '#38bdf8';
    for(let i=0; i<limit; i++) { const p = rawData.map_points[i]; ctxL.fillRect((p.x1/1000)*600, p.y1, 2, 2); ctxR.fillRect((p.x1/1000)*600, p.y2, 2, 2); }
    cL.onmousemove = e => handleHover(e, cL, 'dict_fusion', limit); cR.onmousemove = e => handleHover(e, cR, 'stat_fusion', limit);
}

function resetEvolution() { currentIdx = 0; isEvPaused = false; clearInterval(evAnimationId); evAnimationId = setInterval(() => { if(currentIdx < rawData.map_points.length) { drawEvolutionFrame(currentIdx); currentIdx++; } }, 1000); }
function togglePauseEv() { isEvPaused = !isEvPaused; if(isEvPaused) clearInterval(evAnimationId); else evAnimationId = setInterval(() => { if(currentIdx < rawData.map_points.length) { drawEvolutionFrame(currentIdx); currentIdx++; } }, 1000); document.getElementById('evPlayPauseBtn').innerText = isEvPaused?'PLAY':'PAUSE'; }
function manualControlEv(val) { currentIdx = parseInt(val); if(!isEvPaused) togglePauseEv(); drawEvolutionFrame(currentIdx); }
function drawEvolutionFrame(idx) {
    const canvas = document.getElementById('canvasEv'); const ctx = canvas.getContext('2d');
    ctx.clearRect(0,0,1000,600); ctx.fillStyle = '#38bdf8';
    for(let i=0; i<=idx; i++) ctx.fillRect(rawData.map_points[i].x1, rawData.map_points[i].y2, 3, 3);
    const p = rawData.map_points[idx]; document.getElementById('evSlider').value = idx;
    document.getElementById('evTimer').innerText = p.a + ' | N.' + p.c; canvas.onmousemove = e => handleHover(e, canvas, 'stat', idx+1);
}

function resetFuture() { futPoints = []; isFutPaused = false; document.getElementById('future-panel').innerHTML = ''; animateFuture(); }
function togglePauseFut() { isFutPaused = !isFutPaused; if(!isFutPaused) animateFuture(); document.getElementById('futPlayBtn').innerText = isFutPaused?'PLAY':'PAUSE'; }
function manualControlFut(val) { if(!isFutPaused) togglePauseFut(); const target = parseInt(val); while(futPoints.length < target) generateFutPoint(); while(futPoints.length > target) futPoints.pop(); renderFuture(); }
function generateFutPoint() {
    const u1 = Math.random(), u2 = Math.random();
    const z0 = Math.sqrt(-2.0 * Math.log(u1)) * Math.cos(2.0 * Math.PI * u2);
    const sum = 273 + (z0 * 42);
    const nums = []; while(nums.length<6) { const n=1+Math.floor(Math.random()*90); if(!nums.includes(n)) nums.push(n); }
    nums.sort((a,b)=>a-b); const idx = Math.floor(Math.random()*622614630);
    const p = {x: idx%1000, y: Math.max(0, Math.min(600, ((sum-21)/504)*600)), n: nums, s: Math.round(sum)};
    futPoints.push(p);
    if(futPoints.length < 500 && futPoints.length % 50 === 0) {
        const panel = document.getElementById('future-panel');
        panel.innerHTML = `<div class="fut-row">Sestina: ${p.n.join(' ')}\nSomma: ${p.s}</div>` + panel.innerHTML;
    }
}
function animateFuture() { if(isFutPaused) return; for(let i=0; i<200; i++) if(futPoints.length < 150000) generateFutPoint(); renderFuture(); if(futPoints.length < 150000) futAnimationId = requestAnimationFrame(animateFuture); }
function renderFuture() {
    const canvas = document.getElementById('canvasFut'); const ctx = canvas.getContext('2d');
    ctx.clearRect(0,0,1000,600); ctx.fillStyle = 'rgba(168,85,247,0.15)'; ctx.fillRect(0, ((250-21)/504)*600, 1000, ((300-250)/504)*600);
    ctx.fillStyle = '#38bdf8'; rawData.map_points.forEach(p => ctx.fillRect(p.x1, p.y2, 2, 2));
    ctx.fillStyle = 'var(--fut)'; futPoints.forEach(p => ctx.fillRect(p.x, p.y, 1, 1));
    document.getElementById('futTimer').innerText = 'SIMULAZIONE: +' + futPoints.length;
    document.getElementById('futSlider').value = futPoints.length;
}

function exportFuture() {
    let content = "# EXPORT SIMULAZIONE EXTREME\n# Totale: " + futPoints.length + " combinazioni\n\n";
    futPoints.forEach(p => { content += "Sestina: " + p.n.join(' ') + "\nSomma: " + p.s + "\n\n"; });
    const blob = new Blob([content], {type: 'text/markdown'});
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href = url; a.download = 'gauss_extreme_' + Date.now() + '.md'; a.click();
}

function importFuture(event) {
    const file = event.target.files[0]; if(!file) return;
    document.getElementById('loading-overlay').style.display = 'flex';
    const reader = new FileReader();
    reader.onload = function(e) {
        const text = e.target.result;
        const lines = text.split('\n');
        futPoints = [];
        let currentSestina = null;
        for(let line of lines) {
            if(line.startsWith('Sestina:')) currentSestina = line.replace('Sestina:', '').trim().split(' ').map(Number);
            else if(line.startsWith('Somma:') && currentSestina) {
                const somma = parseInt(line.replace('Somma:', '').trim());
                const idx = Math.floor(Math.random()*622614630);
                futPoints.push({x: idx%1000, y: Math.max(0, Math.min(600, ((somma-21)/504)*600)), n: currentSestina, s: somma});
                currentSestina = null;
            }
        }
        document.getElementById('loading-overlay').style.display = 'none';
        renderFuture();
        alert('Caricate ' + futPoints.length + ' combinazioni nel motore grafico!');
    };
    reader.readAsText(file);
}

function handleHover(e, canvas, mode, limit) {
    const rect = canvas.getBoundingClientRect(); const mx = (e.clientX-rect.left) * (canvas.width / rect.width); const my = (e.clientY-rect.top) * (canvas.height / rect.height);
    const tool = document.getElementById('tooltip'); let found = null;
    const points = (mode==='dict' || mode==='stat') ? rawData.map_points : (mode==='dict_fusion' || mode==='stat_fusion' ? rawData.map_points : []);
    if(points.length === 0) return;
    for(let i=0; i<limit; i++) {
        const p = points[i]; let px, py;
        if(mode==='dict') {px=p.x1; py=p.y1;} else if(mode==='stat') {px=p.x1; py=p.y2;}
        else if(mode==='dict_fusion') {px=(p.x1/1000)*600; py=p.y1;} else if(mode==='stat_fusion') {px=(p.x1/1000)*600; py=p.y2;}
        if(Math.abs(px-mx)<5 && Math.abs(py-my)<5) { found=p; break; }
    }
    if (found) {
        tool.style.display='block'; tool.style.left=(e.pageX+15)+'px'; tool.style.top=(e.pageY+15)+'px';
        tool.innerHTML = `<div style="color:var(--accent);font-weight:700">CONCORSO ${found.c}</div>
            <div style="display:flex;gap:4px;margin:5px 0">${found.n.map(n=>`<span class="ball active" style="width:20px;height:20px;font-size:0.65rem">${n}</span>`).join('')}</div>
            <div style="color:var(--text-dim);font-size:0.6rem">Somma: ${found.sum}</div>`;
    } else tool.style.display='none';
}

function updateDashboard() {
    const yr = document.getElementById('yearSelect').value;
    let stats = {}; 
    if(yr==='ALL') { 
        for(let n=1; n<=90; n++) stats[n]=rawData.global_stats[n].freq; 
        document.getElementById('hotTitle').innerText = 'HOT NUMBERS (GLOBAL)';
        document.getElementById('coldTitle').innerText = 'COLD NUMBERS (GLOBAL)';
    } else { 
        stats=rawData.years_data[yr].freq; 
        document.getElementById('hotTitle').innerText = 'HOT NUMBERS ('+yr+')';
        document.getElementById('coldTitle').innerText = 'COLD NUMBERS ('+yr+')';
    }
    const sorted = Object.entries(stats).sort((a,b)=>b[1]-a[1]);
    const ctxF = document.getElementById('freqChart');
    if(freqChart && typeof freqChart.destroy === 'function') { freqChart.destroy(); }
    freqChart = new Chart(ctxF, { type: 'bar', data: { labels: sorted.slice(0,15).map(x=>'N.'+x[0]), datasets: [{ label: 'Freq', data: sorted.slice(0,15).map(x=>x[1]), backgroundColor: '#38bdf8' }] }, options: { plugins: { legend:{display:false} }, scales: { y: { grid: {color:'#2d3748'} } } } });
    document.getElementById('hotList').innerHTML = ''; sorted.slice(0,10).forEach(x=> document.getElementById('hotList').innerHTML += `<li style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid #2d3748"><span><span class="ball active">${x[0]}</span></span> <span>${x[1]}</span></li>`);
    document.getElementById('coldList').innerHTML = ''; sorted.slice(-10).reverse().forEach(x=> document.getElementById('coldList').innerHTML += `<li style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid #2d3748"><span><span class="ball">${x[0]}</span></span> <span>${x[1]}</span></li>`);
    const delEl = document.getElementById('delayedList'); delEl.innerHTML = '';
    if(yr==='ALL') { Object.entries(rawData.global_stats).sort((a,b)=>b[1].delay-a[1].delay).slice(0,10).forEach(x=> delEl.innerHTML += `<li style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid #2d3748"><span><span class="ball active">${x[0]}</span></span> <span>${x[1].delay}</span></li>`); }
}

// Avvio
window.onload = () => {
    if (typeof rawData !== 'undefined') {
        initYearSelect();
        updateDashboard();
    }
};
