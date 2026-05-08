# 🚀 GUIDA AL CARICAMENTO SU GITHUB

Questa guida ti accompagnerà passo dopo passo nella creazione del tuo repository pubblico.

## 🛠 Fase 1: Preparazione (Da fare una sola volta)
- [ ] Scarica e installa Git se non lo hai già: [git-scm.com](https://git-scm.com/)
- [ ] Apri PowerShell nella cartella `C:\Users\robin\Desktop\super`
- [ ] Configura Git con i tuoi dati:
  ```powershell
  git config --global user.name "robinandreoni87"
  git config --global user.email "robinandreoni@gmail.com"
  ```

## 📂 Fase 2: Organizzazione File
Abbiamo creato molti file. Per un repository professionale, seguiamo questa struttura:
- [ ] Crea una cartella `data/` e sposta dentro i file `estrazioniYYYY.txt`
- [ ] Crea una cartella `simulazioni/` e sposta dentro i file `probabilita_batch_X.md` e `gauss_complete_80_EXTREME.md`
- [ ] Mantieni `genera_dashboard.py`, `dashboard_statistica.html` e il nuovo `README.md` nella root (cartella principale).

## ☁️ Fase 3: Creazione Repo su GitHub.com
- [ ] Vai su [github.com/new](https://github.com/new) (assicurati di essere loggato come `robinandrioli@gmail.com`)
- [ ] Nome Repository: `superenalotto-galactic-mapping`
- [ ] Descrizione: `Interactive Statistical Dashboard and Gaussian Simulation for SuperEnalotto lottery data (1997-2026).`
- [ ] Imposta come **Public**
- [ ] **NON** aggiungere README, .gitignore o licenza (li caricheremo noi dal PC).
- [ ] Clicca su **Create repository**.

## 💻 Fase 4: Comandi di Caricamento (In PowerShell)
Lancia questi comandi uno alla volta:
```powershell
# Inizializza il progetto locale
git init

# Aggiungi tutti i file
git add .

# Crea il primo commit (il "salvataggio" della versione 1.0)
git commit -m "Initial commit: Professional Dashboard v5.7 with Extreme Gaussian Simulation"

# Collega il tuo PC a GitHub (Sostituisci [LINK] con l'URL che ti darà GitHub, es. https://github.com/RobinAndrioli/superenalotto-galactic-mapping.git)
git remote add origin [LINK_DEL_TUO_REPO]

# Rinomina il branch principale
git branch -M main

# Sposta tutto online!
git push -u origin main
```

## 🌐 Fase 5: Dashboard Online (GitHub Pages)
Una volta caricato tutto:
- [ ] Vai nelle **Settings** del tuo repository su GitHub.
- [ ] Clicca su **Pages** nel menu a sinistra.
- [ ] Sotto "Build and deployment", imposta la sorgente su **Deploy from a branch**.
- [ ] Seleziona il branch `main` e la cartella `/(root)`.
- [ ] Clicca su **Save**. 
- [ ] Dopo pochi minuti, la tua dashboard sarà visibile a un link pubblico tipo: `https://robinandrioli.github.io/superenalotto-galactic-mapping/dashboard_statistica.html`

---
*Io sono qui per aiutarti a risolvere ogni errore durante questi passaggi. Dimmi pure quando sei pronto a iniziare!*
