# Metodo, fonti e limiti

## Decisioni implementate

La geometria del Mahjong resta un vincolo reale; il successo linguistico non viene confuso con la difficoltà spaziale. Ogni unità introduce un elemento con esempi e una regola adattata alla lingua. La pratica alterna significato, ascolto, ordine delle parole e produzione guidata. Gli aiuti non consumano accesso all'ascolto e non cancellano vite. Alla fine vengono mostrati regola, modelli corretti, errori/aiuti e occasioni di miglioramento.

La memoria è indicizzata per direzione, modalità e frase. Non si tratta l'abbinamento corretto come prova di scrittura libera, né la trascrizione letta come comprensione orale senza testo. Non si aumenta lo stadio di ritenzione per ripetizioni immediate nello stesso giorno. Le frasi nuove vengono mescolate con esempi precedenti nel Mahjong di abbinamento.

## Evidenza usata e ciò che non dimostra

**Kim & Webb (2022), The Effects of Spaced Practice on Second Language Learning: A Meta-Analysis, Language Learning, 72, 269–319.** Sintesi di 48 esperimenti, 98 effetti, 3.411 partecipanti. Sostiene l'utilità della pratica distanziata, con effetti dipendenti dalle caratteristiche della pratica e dal momento della verifica. Non determina un calendario universale e non valida Parola come prodotto.

https://onlinelibrary.wiley.com/doi/10.1111/lang.12479

**Karpicke & Roediger (2008), The Critical Importance of Retrieval for Learning, Science, 319, 966–968.** Riferimento per distinguere il tentativo di ricordare dalla sola esposizione ripetuta. La nostra produzione con tessere rimane aiutata rispetto alla scrittura senza banca di parole.

https://pubmed.ncbi.nlm.nih.gov/18276894/

**Council of Europe, CEFR Companion Volume.** Cornice per distinguere ricezione, produzione, interazione e mediazione. Questo gioco non comprende ancora una valutazione completa di conversazione spontanea, produzione orale, lettura estesa o mediazione. XP, stelle e completamento del percorso non equivalgono a certificazioni A1–C2.

https://www.coe.int/en/web/common-european-framework-reference-languages/cefr-companion-volume-and-its-language-versions

## Valutazione da fare prima di dichiarare maggiore efficacia

Confrontare versioni a parità di tempo di studio; verificare ritenzione dopo intervalli e trasferimento a frasi non già viste. Separare ascolto da testo, risposte autonome da aiutate e accuratezza da velocità. Revisionare manualmente traduzioni, contesti, varianti e pronuncia con persone competenti nelle singole lingue. Registrare gli errori di riconoscimento del correttore senza etichettare automaticamente come scorrette tutte le risposte fuori inventario. Non sono stati condotti esperimenti di apprendimento su persone per questa build.

## Documentazione tecnica primaria

Piper Python API: caricamento del modello e sintesi WAV.
https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/API_PYTHON.md

Piper CLI e download delle voci.
https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/CLI.md

Scheda della voce araba Kareem: verificare anche la licenza del dataset collegato, non dedurla dal solo repository del software.
https://huggingface.co/rhasspy/piper-voices/blob/main/ar/ar_JO/kareem/medium/MODEL_CARD

Sintesi eSpeak usata per i file effettivamente presenti.
https://espeak.sourceforge.net/commands.html

Il pacchetto non redistribuisce modelli vocali, librerie TTS o font. I modelli e il software per generare nuove voci richiedono le rispettive verifiche di licenza. Il file HTML non contiene credenziali o servizi esterni incorporati.
