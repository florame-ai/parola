# Parola 6.0.2 — Mahjong delle lingue

## Apri il gioco

Apri **index.html** con un browser. Il file consegnato incorpora il gioco e i 566 MP3 disponibili: non occorre installare librerie per giocare.

Questa v6 è stata ricostruita dai sorgenti v5 effettivamente disponibili. Non è il recupero del vecchio archivio v6 citato in chat, che non era presente. La versione 6.0.2 è pubblicata su GitHub Pages: https://florame-ai.github.io/parola/. Sorgenti: https://github.com/florame-ai/parola. Gli aggiornamenti sono descritti in CHANGELOG.md e nella pagina pubblica changelog.html.

## Modifiche reali rispetto alla v5

- **Scrivi e abbina**: scrivi la frase nella lingua di studio per scoprire una tessera; poi abbinala rispettando le regole del Mahjong. Una risposta errata non rimuove tessere. Dopo due tentativi non riconosciuti compare un modello. Ascolto e modello sono aiuti gratuiti, ma la risposta viene registrata come assistita.
- Cinque modalità per ogni unità: Abbina, Ascolta, Completa, Componi, Scrivi e abbina. La schermata percorso e il pulsante di continuazione tengono conto del quinto modo.
- **Ripasso corretto**: una risposta riuscita prima della scadenza, anche in un giorno diverso, non rinvia la verifica programmata. Le abilità e le direzioni linguistiche rimangono distinte.
- **Salvataggio con copia di recupero**: il salvataggio precedente valido è conservato separatamente; un file principale danneggiato non sostituisce la copia valida. Se la memoria è bloccata o piena, il gioco segnala il problema senza smettere di funzionare.
- Lettura dei progressi v5 sullo stesso indirizzo, senza cancellarli. Importazione/esportazione dei progressi e della partita attiva in JSON. La cronologia per Annulla non è ripristinata dopo la riapertura.
- Traduzioni dei nuovi comandi nelle quattro lingue. 12 direzioni di apprendimento, indipendenti dalla lingua dell'interfaccia. Interfaccia araba da destra a sinistra.
- File statici, percorsi relativi e `.nojekyll` per il successivo caricamento su GitHub Pages. Service worker separato e cache limitata alla cartella del progetto.

Il contenuto resta di **24 unità**, con **72 frasi/significati principali allineati**, vocaboli ed espressioni di supporto. Cinque modalità producono 120 combinazioni di unità/modalità per lingua, non 120 argomenti grammaticali distinti. Non si tratta di un corso esaustivo né di una certificazione di livello linguistico.

## File dell'archivio

- `index.html`: gioco autonomo, con i file audio disponibili incorporati.
- `src/`: motore, interfaccia, audio, salvataggi e CSS modificabili.
- `data/`: corso, traduzioni e richieste audio.
- `audio/`: MP3 e relativo manifesto. Servono per ricostruire il gioco dai sorgenti.
- `scripts/build.py`: costruzione senza dipendenze Python aggiuntive.
- `test/`: test del motore, della persistenza e dell'interfaccia.
- `docs/VERIFICA-LOCALE.json`: risultati e limiti delle verifiche effettivamente eseguite.
- `docs/legacy-v5/`: materiale storico, non istruzioni della v6.
- `sw.js`, `manifest.webmanifest`, `icon.svg`, `.nojekyll`: file per la versione ospitata.

## Ricostruzione

Per ricostruire il sito con gli audio separati:

```sh
python scripts/build.py
```

Per ricostruire anche l'edizione in un solo file:

```sh
python scripts/build.py --standalone Parola-Mahjong-v6.html
```

Per rendere autonomo `index.html` dopo la ricostruzione:

```sh
python scripts/build.py --standalone index.html
```

Il controllo rigoroso della copertura audio si esegue con:

```sh
python scripts/build.py --require-all-audio
```

**Quest'ultimo controllo attualmente NON passa:** mancano gli MP3 arabi. Il comando lo segnala ed esce senza sovrascrivere il gioco.

## Verifiche originali della versione 6.0.0

Per la pubblicazione 6.0.2 sono stati superati anche 25 controlli sul sito GitHub Pages reale, inclusi localStorage, copia di recupero, MP3 e ricarica offline. Il resoconto attuale è in `docs/PUBBLICAZIONE.md`; i risultati riportati sotto restano quelli storici della versione ricevuta.

- **18 test Node superati**, inclusi grammatica degli abbinamenti, geometria, generazione delle sequenze, copie di recupero, migrazione e regressione del ripasso anticipato.
- **6.320 tavoli simulati**: 4.320 tavoli negli scenari del motore e 2.000 simulazioni con scelte casuali di coppie valide; nessuno stallo osservato in questi scenari.
- **163 controlli Chromium superati** in due suite di interfaccia: 71 nuovi controlli e 92 sui flussi preesistenti. Comprendono 12 partite complete Scrivi e abbina e 36 partite complete nelle altre modalità testuali.
- Riproduzione effettiva di MP3 di prova in italiano, inglese e russo. Le altre partite automatiche disattivano l'audio per accelerare la simulazione e non costituiscono test di ascolto.
- Schermate desktop e mobile arabo controllate visivamente.

**Limite dei test browser:** l'ambiente blocca la navigazione verso il server locale (`ERR_BLOCKED_BY_ADMINISTRATOR`). Le suite eseguite caricano quindi il documento con `set_content` e una memoria di prova dichiarata, non il localStorage su disco. Le verifiche di ricarica, copia di recupero, importazione e migrazione confermano la logica nella simulazione, non il funzionamento su ogni dispositivo. Il test reale di origine/sottocartella/offline è incluso in `test/v6-browser.test.py`, ma in questo ambiente è rimasto bloccato. Non è indicato come superato.

Comandi dei test (richiedono Node oppure Python con Playwright e Chromium, secondo la suite):

```sh
node --test test/*.test.mjs
python test/v6-ui-fixture.test.py
python test/browser.test.py
# Da eseguire in un ambiente che consenta il server locale:
python test/v6-browser.test.py
```

## Limiti da conoscere prima di pubblicare

**L'audio arabo incorporato manca ancora.** Per l'arabo il lettore usa soltanto un'eventuale voce araba disponibile sul dispositivo, e segnala quando non è presente. Non sostituisce la lingua con un'altra. Il requisito di ascolto garantito indipendentemente dal dispositivo nelle quattro lingue non è quindi soddisfatto.

Le tre lingue con MP3 inclusi usano voci sintetiche di base. La pronuncia e i contenuti non hanno una revisione madrelingua certificata. Componi e le risposte scritte riconoscono le frasi e varianti previste; non sono un correttore universale. Il metodo di ripasso è una regola configurabile di progettazione, non la prova di un risultato didattico ottimale.

L'HTML autonomo contiene già i media disponibili; il funzionamento della cache/service worker su GitHub Pages richiede una prova dopo il caricamento. Il browser può rimuovere la cache. L'app non può imporre volume, autorizzazioni audio o disponibilità dell'altoparlante.

## Pubblicazione su GitHub Pages

Estrai lo ZIP e carica i file, non lo ZIP, nella cartella principale del repository. `index.html` deve essere al primo livello. Per usare le funzioni della versione ospitata, mantieni anche `sw.js`, `manifest.webmanifest`, `icon.svg` e `.nojekyll`.

Il repository pubblico `florame-ai/parola` pubblica il ramo `master` dalla cartella radice `/(root)`. Prima di ogni push integrare gli aggiornamenti remoti su master senza forzare il push. Nessun token o segreto deve essere inserito nel sito. La versione ricevuta è conservata in un commit separato.

Esporta i progressi prima di cambiare indirizzo: un file locale e una pagina ospitata non condividono automaticamente lo stesso salvataggio.
