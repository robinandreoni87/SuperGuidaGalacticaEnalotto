
# Progetto: Dashboard di Analisi Statistica SuperEnalotto

Questo documento delinea la struttura e le fasi di sviluppo per la Dashboard professionale richiesta, focalizzata sullo studio statistico dei dati estratti dal 2009 al 2026+.

## 1. Architettura del Sistema
Il sistema sarà diviso in due parti principali:
- **Data Processor (Il Motore)**: Uno script che scansiona la cartella dei file `.txt`, ne analizza il contenuto e genera un database leggero (JSON) con tutte le statistiche calcolate.
- **Analytic Dashboard (L'Interfaccia)**: Una pagina HTML singola, moderna e reattiva, che visualizza i dati attraverso grafici e tabelle intelligenti.

## 2. Analisi Statistica Approfondita
Il programma calcolerà i seguenti dati per ogni numero (1-90), Jolly e SuperStar:
- **Frequenza Assoluta**: Quante volte è uscito un numero dal 2009 ad oggi.
- **Ritardo Attuale**: Da quanti concorsi non esce un determinato numero.
- **Ritardo Massimo**: Il record storico di assenza per ogni numero.
- **Frequenza per Anno**: Analisi del "trend" di uscita (es. il numero 15 usciva molto nel 2015 ma poco nel 2024?).
- **Analisi delle Coppie/Terzine**: Quali numeri tendono a uscire insieme più spesso.
- **Distribuzione Pari/Dispari**: Studio statistico della composizione delle sestine.

## 3. Design della Dashboard (Estetica Premium)
L'interfaccia seguirà i canoni del design moderno:
- **Tema Dark/Glassmorphism**: Sfondo scuro con elementi in vetro sfocato per un look professionale.
- **Grafici Interattivi**: Possibilità di filtrare i dati per anno o per range di concorsi.
- **Indicatori di Performance**: "Semafori" o icone per indicare i numeri più caldi (Hot Numbers) e quelli più ritardatari (Cold Numbers).

## 4. Roadmap di Sviluppo
1. **Fase 1**: Creazione dello script di parsing che legge i file `.txt` e valida i dati (gestione errori per file incompleti o corrotti).
2. **Fase 2**: Implementazione dell'algoritmo statistico per il calcolo di frequenze e ritardi.
3. **Fase 3**: Sviluppo dell'interfaccia HTML/CSS con integrazione di Chart.js per la parte visuale.
4. **Fase 4**: Test di caricamento dinamico (assicurarsi che se l'utente aggiunge `estrazioni2008.txt`, la dashboard lo includa automaticamente al prossimo avvio).

## 5. Note Tecniche
- Il programma deve gestire i ritardi di caricamento del sito originale (già implementato nel bot v2.0).
- I dati saranno estratti rispettando l'ordine cronologico (estrazioni a scaletta).
- Nessuna dipendenza esterna complessa: deve funzionare in modo agile sul sistema dell'utente.

---
**STATO ATTUALE**: In attesa di conferma dell'utente sulla struttura per procedere con il codice.
