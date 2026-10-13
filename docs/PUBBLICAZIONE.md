# Pubblicazione di Parola 6.0.1

Data: 13 ottobre 2026.

- Repository pubblico: https://github.com/florame-ai/parola-mahjong
- Gioco: https://florame-ai.github.io/parola-mahjong/
- Aggiornamenti: https://florame-ai.github.io/parola-mahjong/changelog.html
- GitHub Pages: ramo master, cartella radice, HTTPS attivo.
- Primo caricamento verificato: risposta HTTP 200 e metadati versione 6.0.1.

## Verifiche eseguite in questa pubblicazione

18 test Node superati, compresi motore, persistenza, migrazione e ripasso anticipato. Le simulazioni del motore hanno prodotto 4.320 scenari e 2.000 partite con scelte casuali valide senza stalli osservati.

25 controlli Chromium superati prima sull'origine locale reale, poi sull'indirizzo pubblico GitHub Pages:

- Avvio, numero versione, 24 unità e cinque modalità.
- Riproduzione effettiva di MP3 in italiano, inglese e russo.
- Persistenza della partita dopo ricarica con localStorage reale.
- Recupero del salvataggio principale danneggiato dalla copia di backup.
- 12 partite Scrivi e abbina completate, una per direzione linguistica.
- Layout mobile nelle quattro lingue dell'interfaccia, con controllo RTL arabo e assenza di overflow orizzontale.
- Ricarica del gioco e riproduzione MP3 con rete disattivata.
- Apertura del changelog pubblico con rete disattivata.
- Assenza di errori JavaScript e traduzioni mancanti durante la suite.

Report: `local-pages-verification-6.0.1.json` e `pages-verification-6.0.1.json`. Schermate: `pages-desktop-6.0.1.png` e `pages-mobile-6.0.1.png`. Questi controlli verificano Chromium in questo ambiente; i report originali della versione 6.0.0 restano conservati come evidenza storica e non descrivono la verifica attuale.

## Limiti mantenuti

Gli MP3 arabi sono ancora assenti. Il gioco usa una voce araba del dispositivo, se disponibile. Non è stata eseguita una revisione madrelingua dei contenuti. Per spostare i progressi dal file locale al sito occorre esportarli e importarli dalle Impostazioni.

## Conservazione e aggiornamenti

Il commit iniziale conserva integralmente la versione 6.0.0 ricevuta. Un secondo commit prepara la release 6.0.1 e un terzo conserva la verifica pubblica. I push avvengono su master dopo aver recuperato e integrato gli aggiornamenti remoti, senza forzature. `CHECKSUMS.sha256` elenca i file attualmente conservati.
