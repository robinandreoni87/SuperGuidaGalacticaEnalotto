
# Configurazione
$targetDir = "C:\Users\robin\Desktop\super\"
if (!(Test-Path $targetDir)) { New-Item -ItemType Directory -Path $targetDir }

$startYear = 2009
$currentYear = 2026
$months = @("gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre")
$userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

Write-Host "=== AVVIO ESTRATTORE INTELLIGENTE v2.0 ===" -ForegroundColor Yellow
Write-Host "Destinazione: $targetDir`n" -ForegroundColor Gray

for ($year = $startYear; $year -le $currentYear; $year++) {
    $outputFile = Join-Path $targetDir "estrazioni$year.txt"
    $isCurrentYear = ($year -eq $currentYear)
    
    # Verifica se l'anno è già stato completato
    if (Test-Path $outputFile) {
        $fileContent = Get-Content $outputFile -Raw -ErrorAction SilentlyContinue
        
        if (-not $isCurrentYear) {
            # Per gli anni passati, controlliamo se c'è "Dicembre" nel file
            # Se c'è, consideriamo l'anno finito e saltiamo
            if ($fileContent -like "*Dicembre $year*") {
                Write-Host "[SKIP] Anno $year già completo." -ForegroundColor DarkCyan
                continue
            }
            else {
                Write-Host "[INFO] Anno $year incompleto o mancante. Ripristino in corso..." -ForegroundColor Yellow
                Remove-Item $outputFile
            }
        }
        else {
            # Per l'anno corrente, lo riscriviamo sempre per avere gli ultimi dati
            Write-Host "[UPDATE] Aggiornamento anno corrente $year..." -ForegroundColor Cyan
            Remove-Item $outputFile
        }
    }

    Write-Host "[START] Estrazione Anno $year..." -ForegroundColor Cyan
    $contentForYear = ""

    foreach ($month in $months) {
        $url = "https://www.superenalotto.it/archivio-estrazioni/$year/$month"
        
        $maxRetries = 5 # Aumentato a 5 tentativi
        $retryCount = 0
        $success = $false
        $html = ""

        while (-not $success -and $retryCount -lt $maxRetries) {
            try {
                # Aumentato timeout per connessioni lente
                $response = Invoke-WebRequest -Uri $url -UserAgent $userAgent -TimeoutSec 20 -ErrorAction Stop
                $html = $response.Content
                $success = $true
            }
            catch {
                $retryCount++
                Write-Host " [RETRY $retryCount/$maxRetries] Problema con ${month} ${year}. Attendo 3 secondi..." -ForegroundColor Yellow
                Start-Sleep -Seconds 3
            }
        }

        if ($success) {
            $rowRegex = '(?s)<tr class="superenalotto-extraction-archive__details__table__row.*?</tr>'
            $rows = [regex]::Matches($html, $rowRegex)

            if ($rows.Count -gt 0) {
                Write-Host " -> ${month}: Estratti $($rows.Count) concorsi." -ForegroundColor Green
                foreach ($row in $rows) {
                    $rowContent = $row.Value
                    
                    $labelRegex = 'Concorso\s+<strong>N.*?(\d+)</strong>\s+del\s+<strong>(.*?)</strong>'
                    $labelMatch = [regex]::Match($rowContent, $labelRegex)
                    $nConcorso = $labelMatch.Groups[1].Value.Trim()
                    $dataConcorso = $labelMatch.Groups[2].Value.Trim()
                    
                    $compRegex = '(?s)superenalotto-extraction-archive__details__table__combination.*?text">(.*?)</span>'
                    $compMatches = [regex]::Matches($rowContent, $compRegex)
                    $numeri = @()
                    foreach ($m in $compMatches) { if ($m.Groups[1].Value.Trim()) { $numeri += $m.Groups[1].Value.Trim() } }
                    
                    $jollyRegex = 'superenalotto-extraction-archive__details__table__jolly.*?text">(.*?)</span>'
                    $jollyMatch = [regex]::Match($rowContent, $jollyRegex)
                    $jolly = $jollyMatch.Groups[1].Value.Trim()
                    
                    $superstarRegex = 'superenalotto-extraction-archive__details__table__superstar.*?text">(.*?)</span>'
                    $superstarMatch = [regex]::Match($rowContent, $superstarRegex)
                    $superstar = $superstarMatch.Groups[1].Value.Trim()

                    if ($nConcorso -and $numeri.Count -ge 6) {
                        $contentForYear += "Nº $nConcorso - Concorso del $dataConcorso`r`n"
                        $contentForYear += "Numeri: $($numeri -join ' ')`r`n"
                        $contentForYear += "Jolly: $jolly`r`n"
                        $contentForYear += "SuperStar: $superstar`r`n"
                        $contentForYear += "--------------------------------------`r`n"
                    }
                }
                # Salvataggio progressivo
                $contentForYear | Out-File -FilePath $outputFile -Encoding utf8
            }
        }
    }
    if ($contentForYear) {
        Write-Host "[OK] Anno $year salvato correttamente.`n" -ForegroundColor White
    }
}

Write-Host "=== ARCHIVIO COMPLETO AGGIORNATO ===" -ForegroundColor Yellow
