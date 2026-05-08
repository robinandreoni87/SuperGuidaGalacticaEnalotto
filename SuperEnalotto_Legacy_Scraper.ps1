
# Configurazione
$targetDir = "C:\Users\robin\Desktop\super\"
if (!(Test-Path $targetDir)) { New-Item -ItemType Directory -Path $targetDir }

$startYear = 1997
$endYear = 2008
$userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"

Write-Host "=== AVVIO ESTRATTORE STORICO CORRETTO (1997-2008) ===" -ForegroundColor Yellow
Write-Host "Sorgente: superenalotto.net`n" -ForegroundColor Gray

for ($year = $endYear; $year -ge $startYear; $year--) {
    $outputFile = Join-Path $targetDir "estrazioni$year.txt"
    
    # Regola Dicembre: se l'anno è già completo, saltiamo
    if (Test-Path $outputFile) {
        $fileContent = Get-Content $outputFile -Raw -ErrorAction SilentlyContinue
        if ($fileContent -like "*dicembre $year*") {
            Write-Host "[SKIP] Anno $year già completo." -ForegroundColor DarkCyan
            continue
        }
        else {
            Write-Host "[INFO] Anno $year incompleto o vuoto. Ripristino in corso..." -ForegroundColor Yellow
            Remove-Item $outputFile
        }
    }

    Write-Host "[START] Estrazione Anno $year..." -ForegroundColor Cyan
    $url = "https://www.superenalotto.net/estrazioni/$year"
    
    try {
        $response = Invoke-WebRequest -Uri $url -UserAgent $userAgent -TimeoutSec 30 -ErrorAction Stop
        $html = $response.Content
        
        # Regex più flessibile per le righe (cerca tr che contengono drawNumber)
        $rows = [regex]::Matches($html, '(?s)<tr>.*?drawNumber.*?</tr>')
        
        if ($rows.Count -gt 0) {
            Write-Host " -> Trovati $($rows.Count) concorsi. Analisi in corso..." -ForegroundColor Gray
            $contentForYear = ""

            foreach ($row in $rows) {
                $rowHtml = $row.Value
                
                # 1. Estrazione Concorso (es: 157/08 -> 157)
                $nConcorso = ""
                if ($rowHtml -match 'drawNumber".*?>(\d+)') { 
                    $nConcorso = $matches[1] 
                }
                
                # 2. Estrazione Data (pulisce il tag span e prende il resto)
                $dataConcorso = ""
                if ($rowHtml -match 'class="date.*?"><span>.*?</span>\s*(.*?)</td>') {
                    $dataConcorso = $matches[1].Trim() + " $year"
                }

                # 3. Estrazione Numeri (analizziamo le celle ballCell)
                $cellMatches = [regex]::Matches($rowHtml, '(?s)<td class="ballCell">.*?</td>')
                
                if ($cellMatches.Count -ge 2) {
                    # Cella 1: I 6 numeri principali
                    $numeri = @()
                    $numMatches = [regex]::Matches($cellMatches[0].Value, '<li>(\d+)</li>')
                    foreach ($nm in $numMatches) { $numeri += $nm.Groups[1].Value }
                    
                    # Cella 2: Il numero Jolly
                    $jolly = ""
                    if ($cellMatches[1].Value -match 'class="jolly">(\d+)</li>') { 
                        $jolly = $matches[1] 
                    }
                    
                    # Cella 3: SuperStar (presente solo dal 2006)
                    $superstar = ""
                    if ($cellMatches.Count -ge 3) {
                        if ($cellMatches[2].Value -match 'class="superstar">(\d+)</li>') {
                            $superstar = $matches[1]
                        }
                    }

                    if ($nConcorso -and $numeri.Count -ge 6) {
                        $contentForYear += "Nº $nConcorso - Concorso del $dataConcorso`r`n"
                        $contentForYear += "Numeri: $($numeri[0..5] -join ' ')`r`n"
                        $contentForYear += "Jolly: $jolly`r`n"
                        $contentForYear += "SuperStar: $superstar`r`n"
                        $contentForYear += "--------------------------------------`r`n"
                    }
                }
            }
            
            if ($contentForYear) {
                $contentForYear | Out-File -FilePath $outputFile -Encoding utf8
                Write-Host "[OK] Anno $year salvato correttamente.`n" -ForegroundColor White
            }
            else {
                Write-Host " [!] Errore: Dati non estratti per l'anno $year. Verificare HTML." -ForegroundColor Red
            }
        }
        else {
            Write-Host " [!] Nessun concorso trovato per l'anno $year." -ForegroundColor Red
        }
    }
    catch {
        Write-Host " [ERRORE] Impossibile collegarsi al sito per l'anno $year." -ForegroundColor Red
    }
    
    # Pausa di 3 secondi per sicurezza e feedback costante
    Start-Sleep -Seconds 3
}

Write-Host "`n=== LAVORO COMPLETATO ===" -ForegroundColor Yellow
