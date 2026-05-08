import random
import os

def generate_gaussian_sestina(mu, sigma, seen):
    while True:
        target_sum = round(random.gauss(mu, sigma))
        if target_sum < 21 or target_sum > 525:
            continue
        
        nums = []
        while len(nums) < 5:
            n = random.randint(1, 90)
            if n not in nums:
                nums.append(n)
        
        last_n = target_sum - sum(nums)
        if 1 <= last_n <= 90 and last_n not in nums:
            nums.append(last_n)
            nums.sort()
            s_str = " ".join(map(str, nums))
            if s_str not in seen:
                seen.add(s_str)
                return s_str, sum(nums)

def create_massive_gauss(base_path, count):
    filename = "gauss_complete_80_EXTREME.md"
    filepath = os.path.join(base_path, filename)
    print(f"Generazione EXTREME: {filename} ({count} combinazioni)...")
    seen = set()
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# SIMULAZIONE MASSIVA EXTREME - COMPLETAMENTO GAUSS 80%\n")
        f.write(f"# Totale Combinazioni: {count}\n\n")
        for i in range(count):
            if i % 25000 == 0 and i > 0:
                print(f"Processati {i}...")
            s_str, somma = generate_gaussian_sestina(273, 42, seen)
            f.write(f"Sestina: {s_str}\n")
            f.write(f"Somma: {somma}\n\n")
    print(f"File generato con successo: {filepath}")
    # Calcolo approssimativo dimensione
    size_mb = os.path.getsize(filepath) / (1024 * 1024)
    print(f"Dimensione file: {size_mb:.2f} MB")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    base_path = os.path.join(base_dir, "simulations")
    if not os.path.exists(base_path): os.makedirs(base_path)
    create_massive_gauss(base_path, 150000)
