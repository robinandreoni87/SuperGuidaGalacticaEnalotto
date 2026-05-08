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

def create_batch(base_path, batch_num, count, mu, sigma, seen):
    filename = f"probabilita_batch_{batch_num}.md"
    filepath = os.path.join(base_path, filename)
    print(f"Generazione {filename}...")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# SIMULAZIONE FUTURISTICA - BATCH {batch_num}\n")
        f.write(f"# Distribuzione Gaussiana | Somma Media: {mu}\n\n")
        for _ in range(count):
            s_str, somma = generate_gaussian_sestina(mu, sigma, seen)
            f.write(f"Sestina: {s_str}\n")
            f.write(f"Somma: {somma}\n\n")

if __name__ == "__main__":
    base_path = r"C:\Users\robin\Desktop\super"
    all_seen = set()
    
    # Generiamo 5 file da 2000 sestine ciascuno (Totale 10.000 nuove probabilità)
    for i in range(1, 6):
        create_batch(base_path, i, 2000, 273, 50, all_seen)
    
    print("Tutti i 5 batch sono stati creati con successo!")
