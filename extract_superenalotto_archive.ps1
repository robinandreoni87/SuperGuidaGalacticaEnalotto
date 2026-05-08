
$years = @(2023, 2024, 2025, 2026)
$months = @("gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre")
$userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

foreach ($year in $years) {
    $outputFile = "estrazioni$year.txt"
    Write-Host "`n=== ESTRAZIONE ANNO $year ===" -ForegroundColor Cyan
    
    # Pulisce il file se esiste
    if (Test-Path $outputFile) { Remove-Item $outputFile }
    
    foreach ($month in $months) {
        $url = "https://www.superenalotto.it/archivio-estrazioni/$year/$month"
        Write-Host "Scaricando $month $year..." -ForegroundColor Gray -NoNewline
        
        try {
            $response = Invoke-WebRequest -Uri $url -UserAgent $userAgent -ErrorAction Stop
            $html = $response.Content
            
            # Regex per le righe delle estrazioni
            $rowRegex = '(?s)<tr class="superenalotto-extraction-archive__details__table__row.*?</tr>'
            $rows = [regex]::Matches($html, $rowRegex)
            
            if ($rows.Count -eq 0) {
                Write-Host " [Nessun dato]" -ForegroundColor Gray
                continue
            }
            
            Write-Host " [$($rows.Count) concorsi]" -ForegroundColor Green
            
            foreach ($row in $rows) {
                $rowContent = $row.Value
                
                # 1. Concorso e Data
                $labelRegex = 'Concorso\s+<strong>N.*?(\d+)</strong>\s+del\s+<strong>(.*?)</strong>'
                $labelMatch = [regex]::Match($rowContent, $labelRegex)
                $nConcorso = $labelMatch.Groups[1].Value.Trim()
                $dataConcorso = $labelMatch.Groups[2].Value.Trim()
                
                # 2. Combinazione
                $compRegex = '(?s)superenalotto-extraction-archive__details__table__combination.*?text">(.*?)</span>'
                $compMatches = [regex]::Matches($rowContent, $compRegex)
                $numeri = @()
                foreach ($m in $compMatches) { 
                    $val = $m.Groups[1].Value.Trim()
                    if ($val) { $numeri += $val }
                }
                
                # 3. Jolly
                $jollyRegex = 'superenalotto-extraction-archive__details__table__jolly.*?text">(.*?)</span>'
                $jollyMatch = [regex]::Match($rowContent, $jollyRegex)
                $jolly = $jollyMatch.Groups[1].Value.Trim()
                
                # 4. SuperStar
                $superstarRegex = 'superenalotto-extraction-archive__details__table__superstar.*?text">(.*?)</span>'
                $superstarMatch = [regex]::Match($rowContent, $superstarRegex)
                $superstar = $superstarMatch.Groups[1].Value.Trim()
                
                # Scrittura su file se i dati sono validi
                if ($nConcorso -and $numeri.Count -ge 6) {
                    $combinazione = $numeri -join " "
                    $blocco = "Nº $nConcorso - Concorso del $dataConcorso`r`n"
                    $blocco += "Numeri: $combinazione`r`n"
                    $blocco += "Jolly: $jolly`r`n"
                    $blocco += "SuperStar: $superstar`r`n"
                    $blocco += "--------------------------------------`r`n"
                    
                    $blocco | Out-File -FilePath $outputFile -Append -Encoding utf8
                }
            }
        }
        catch {
            Write-Host " [Errore/Non disponibile]" -ForegroundColor Gray
        }
    }
}

Write-Host "`nLavoro completato per tutti gli anni!" -ForegroundColor Yellow
