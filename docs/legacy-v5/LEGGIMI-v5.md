# Parola 5 — Mahjong delle lingue

Versione autonoma, ottobre 2026. Il gioco è reale, locale e senza dipendenze di rete durante la partita. **Questo archivio non modifica il sito ChatGPT pubblicato in precedenza.** È costruito a partire dal pacchetto v4 fornito nella conversazione, non dai sorgenti non disponibili della versione pubblicata v3.

## Giocare

L'edizione separata `Parola-Mahjong-v5.html` incorpora codice, contenuti, interfaccia e 566 MP3: aprirla con un browser moderno. Non aprirla come documento di testo. Nell'archivio sorgenti, mantenere `index.html` accanto alla cartella `audio/`.

Per servire questa cartella localmente, da un terminale aperto qui:

```sh
python -m http.server 8080
```

Poi aprire `http://localhost:8080` nel browser. Nessuna registrazione, nessun acquisto e nessun invio delle risposte scritte a servizi esterni. Le voci opzionali del dispositivo possono essere fornite dal sistema operativo o da un servizio del suo produttore; il comportamento di tali voci non è controllato da questo gioco.

## Il Mahjong rimane il gioco

Una tessera si può rimuovere solo quando non è coperta ed è libera a destra o a sinistra. Il tavolo ha strati effettivi. Quattro modalità riusano queste regole:

**Abbina:** collega la frase nella lingua obiettivo al suo significato nella lingua di supporto. **Ascolta:** le tessere obiettivo mostrano una traccia sonora invece della risposta scritta. **Completa:** ogni scelta prova a inserire la parola successiva della frase richiesta. **Componi:** costruisci tre frasi diverse tra le combinazioni previste per l'unità; anche qui l'ordine e la libertà delle tessere contano.

Nelle frasi, quando parole identiche o un ramo alternativo bloccano geometricamente la prosecuzione, un riallineamento automatico conserva le parole disponibili e ripristina una strada. È dichiarato nell'interfaccia e non consuma il rimescolamento: la geometria non deve impedire di completare la lezione. Non equivale a un Mahjong classico senza riassetti.

## Contenuti e lingue: numeri precisi

24 unità, quattro modalità e quattro lingue obiettivo: 96 missioni per lingua, 384 combinazioni unità/modalità/lingua. Italiano, inglese, arabo e russo si possono accoppiare in tutte le 12 direzioni. La lingua dell'interfaccia è indipendente: 48 configurazioni direzione/interfaccia.

Il materiale comprende **72 significati/frasi allineati**, **6 espressioni di supporto**, **60 varianti esplicite** oltre alle forme principali e **238 chiavi UI tradotte in quattro lingue**. Le 384 missioni non rappresentano 384 argomenti grammaticali diversi. Le spiegazioni cambiano con la grammatica della lingua obiettivo e con la lingua di supporto; non sono semplici sostituzioni di etichette.

Il percorso tratta saluti, identità, oggetti, accordi, numeri, possesso, abitudini, negazione, luoghi, richieste, domande, plurali, passato, futuro, possibilità, preferenze, comparazioni, motivazioni, pronomi, relative, condizioni, esperienze e desideri. Le unità finali sono introduzioni con esempi mirati, non un trattamento esaustivo dei casi, delle eccezioni, dei verbi o della competenza comunicativa.

## Audio: ciò che è davvero incluso

566 file MP3 sintetici di base: italiano, inglese e russo. Il player usa i file inclusi come prima scelta, con ripetizione illimitata e velocità 0,8x. Le voci sono eSpeak, quindi non equivalgono a una voce neurale naturale né a registrazioni professionali. Non sono state revisionate all'ascolto da madrelingua.

**Mancano 191 clip arabe.** Il player cerca esclusivamente una voce araba effettiva del dispositivo e, quando non la trova, lo comunica. Non sostituisce l'arabo con persiano, italiano o una traccia muta. Il requisito dell'utente di audio garantito in tutte le lingue **non è ancora soddisfatto** da questo pacchetto. La modalità araba di ascolto richiede una voce araba del dispositivo oppure la generazione del pacchetto mancante.

Il controllo `--require-all-audio` blocca il rilascio completo in presenza di qualsiasi clip mancante, errata o associata a una lingua diversa. La lettura della trascrizione non è registrata come ascolto autonomo.

### Generare un pacchetto neurale corretto

Questa procedura è preparata, non eseguita o verificata con modelli reali in questo ambiente. Richiede un ambiente con accesso Internet per l'installazione e il download iniziale, poi funziona localmente. Leggere prima licenza e scheda del modello, inclusa la licenza del dataset. Non è lecito presumere che tutte le voci abbiano la stessa licenza.

```sh
python -m pip install piper-tts
# Dopo aver esaminato MODEL_CARD/licenza della voce araba:
python -m piper.download_voices ar_JO-kareem-medium --data-dir voices
python scripts/generate_neural_audio.py --lang ar \
  --model voices/ar_JO-kareem-medium.onnx --license-reviewed
# Revisione umana della pronuncia prima del rilascio didattico.
python scripts/build.py --require-all-audio --standalone Parola-Mahjong-v5.html
```

`ffmpeg` deve essere installato. Lo script controlla che la lingua dichiarata dal modello coincida con quella richiesta e non contiene chiavi private. Per migliorare anche le altre lingue, ripetere con un modello corrispondente. I modelli non sono inclusi nell'archivio.

## Aiuti, punteggi e apprendimento

Un suggerimento gratuito e un rimescolamento gratuito per partita di livello. I successivi richiedono una produzione scritta mirata con il significato richiesto. Dopo due tentativi non riconosciuti, o su richiesta, compare un modello guidato: lo scopo non è bloccare chi non riesce ancora. Il testo vuoto non sblocca aiuti. Ascolto, rallentamento e spiegazioni restano gratuiti e non consumano aiuti.

I punti premiano risultati corretti, assenza di aiuti/errori e continuità. Non premiano automaticamente la lunghezza della frase o l'aggiunta di aggettivi. Gli XP di una missione registrano il miglior punteggio: ripeterla uguale non genera XP infiniti. Non ci sono vite da perdere o un obbligo di serie giornaliera.

Ripassi separati per coppia linguistica, abilità e frase. Un risultato corretto autonomo fa crescere lo stadio solo dopo l'intervallo previsto, non dopo ripetizioni immediate nello stesso giorno. Gli intervalli iniziali 1/3/7/14/30 giorni sono euristici, non una sequenza dimostrata ottimale per tutti. Errori e aiuti richiamano presto il materiale. Non si dichiarano livelli CEFR raggiunti né un miglioramento sperimentalmente misurato dell'efficacia dell'app.

`Componi` è una produzione guidata con risposte e varianti esplicite, **non** un correttore universale. Una risposta non riconosciuta non dimostra che sia linguisticamente scorretta. I contenuti sono stati scritti e controllati strutturalmente, ma richiedono revisione linguistica madrelingua prima di un uso educativo certificato.

## Progressi e compatibilità

Il gioco usa la chiave separata `parola-mahjong-v5` nello storage del browser. Non cancella chiavi di versioni precedenti. Si può esportare/importare un JSON v5 dalle impostazioni; il ripristino mantiene il punteggio migliore. L'esportazione conserva progressi, non la partita aperta. Il salvataggio automatico locale conserva invece la partita aperta per ciascuna direzione, inclusi gli aiuti già consumati.

Non è stata implementata una migrazione degli sconosciuti dati della versione v3 pubblicata: non viene inventata compatibilità con uno schema che non è stato fornito. I progressi locali non passano automaticamente tra domini, dispositivi o file diversi. Se il browser non permette storage, il gioco lo segnala e resta disponibile l'esportazione manuale.

## Costruire e verificare

```sh
python scripts/build.py --standalone Parola-Mahjong-v5.html
node --test test/engine.test.mjs
python test/browser.test.py
python test/visual_smoke.py
```

Per i test browser servono Python, Playwright e Chromium. I test cercano prima l'HTML standalone accanto al progetto, poi nella cartella del progetto. In questo ambiente la navigazione URL/file del browser è bloccata: l'interfaccia è stata caricata con `set_content` e lo storage sostituito con una memoria di prova. Non è una verifica della persistenza fisica sul dispositivo dell'utente. I tre test audio iniziali e la prova di ascolto usano MP3 veri senza sostituire il player con mock. Le 36 simulazioni UI dei giochi non-audio silenziano volontariamente il parlato.

Risultati: 8 gruppi di test del motore; 4.320 tavoli completi più 2.000 tavoli con scelte casuali legali, zero stalli osservati; 92 controlli browser, inclusi 36 livelli completati e 48 configurazioni UI/direzione; 566 MP3 decodificati e non silenziosi. Screenshot desktop e mobili in `docs/`. Questi controlli tecnici non sono una validazione didattica o della pronuncia.

## Struttura

`src/engine.mjs`: geometria, abbinamenti, grammatica guidata, memoria e importazione. `src/app.mjs`: esperienza completa. `src/audio.mjs`: file e voci corrispondenti. `src/styles.css`: UI responsive/RTL/movimento ridotto. `data/course.json`: materiale estendibile. `data/ui.json`: localizzazione. `data/audio-requests.json`: inventario dei 757 audio richiesti. `audio/`: file e manifest. `scripts/`: build e produzione audio. `test/`: controlli ripetibili. `docs/`: report, fonti e schermate.

Per aggiungere un'unità: definire tre frasi/significati e varianti, quattro traduzioni, spiegazioni per lingua obiettivo/supporto e gli audio. Tenere separati obiettivo comunicativo, forma grammaticale e difficoltà del tavolo. Non pubblicare un'unità con una traduzione vuota o l'audio richiesto assente.
