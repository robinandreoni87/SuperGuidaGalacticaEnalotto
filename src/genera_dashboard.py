import os
import re
import json
import math

# Configurazione percorsi relativi (Professionale)
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
input_dir = os.path.join(base_dir, "data")
output_data_js = os.path.join(base_dir, "data.js")

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
    if not os.path.exists(input_dir):
        print(f"ERRORE: Cartella dati non trovata in {input_dir}")
        return []
    
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

def generate_data_js(data):
    json_data = json.dumps(data)
    js_content = f"const rawData = {json_data};"
    with open(output_data_js, 'w', encoding='utf-8') as f:
        f.write(js_content)

if __name__ == "__main__":
    print("Analisi file in corso...")
    draws = parse_files()
    if not draws: 
        print("ATTENZIONE: Nessun dato trovato. Assicurati che i file .txt siano nella cartella /data")
    else:
        stats = calculate_stats(draws)
        generate_data_js(stats)
        print(f"File dati aggiornato con successo: {output_data_js}")
        print("La Dashboard (index.html) rifletterà i nuovi dati al prossimo refresh.")
