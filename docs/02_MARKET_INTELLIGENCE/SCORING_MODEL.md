# GTM Engine — Competitive Scoring Model v1.1

**Stato:** specifica matematica sperimentale allegata allo Scope del Modulo 02. Non validata con dataset reali.  
**Versione congelata per il pilota:** 1.1 — parametri ricalibrabili solo in una nuova versione.

## 1. Vincolo architetturale

Ogni azienda ottiene sei score **separati** e autonomi su `[0,100]`:

`S_ij = f_j(dati_azienda_i, parametri_j, mercato_versionato)`.

Non dipendono dai valori delle altre aziende selezionate; aggiungere o rimuovere competitor può cambiare la classifica ma **non gli score già calcolati**, a parità di dati, paniere di keyword e parametri. Non affermare indipendenza *statistica*: le dimensioni possono essere correlate.

## 2. Formule per il prototipo

### 2.1 Positioning

C = chiarezza, D = distintività documentabile, T = pertinenza rispetto al target, E = evidenze. Ciascuno ha rubrica specifica 0–4, ancorata a fatti osservati sul sito.

`S_POS = 25 × (C + D + T + E) / 4`

Le valutazioni non sono relative ai competitor nel progetto. Conservare URL e ragione del giudizio; tre valutazioni AI ripetute e controllo concordanza prima di dichiarare stabile la valutazione. Rubriche dettagliate ancora da specificare nel TDD.

### 2.2 Organic Visibility

Paniere **non-branded**, costruito dalla Demand Intelligence sulla base del mercato, congelato e versionato *prima* del confronto. Ogni keyword q ha volume V e pertinenza R∈[0,1]; profondità SERP N=20 iniziale; posizione organica p.

`g(p) = max(0, (1/log₂(p+1) − 1/log₂(N+2)) / (1 − 1/log₂(N+2)))` per ranking monitorato; `g=0` per assenza **verificata** nei primi N; ranking ignoto/SERP fallita = dato mancante.

`S_SEO = 100 × Σ_q[V_q × R_q × g(p_q)] / Σ_q[V_q × R_q]`

Richiede denominatore >0, volumi/query effettivamente supportati e copertura adeguata. Misura visibilità teorica ponderata, non traffico reale.

### 2.3 Social Performance

Campione fino a 50 post Instagram accessibili e coerenti temporalmente; F = follower osservati, ER = mediana di `(like+commenti)/F` sui post con metriche presenti.

`B(F) = clamp(0,02 × (F/10000)^(-0,15), 0,005, 0,05)`

`S_SOC = 100 × ER / (ER + B(F))`

Esponente −0,15 e soglie sono **non calibrati**. Test sensibilità con −0,10 e −0,20; score sperimentale. Non dedurre vendite dalle interazioni. F>0 obbligatorio.

### 2.4 Advertising Activity

Periodo di osservazione: **12 settimane verificabili** per la misura principale. P = settimane con attività verificata / 12; C = creatività distinte e deduplicate nello stesso periodo.

`H(C) = min(1, ln(1+C) / ln(21))`

`S_ADS = 100 × (0,7 P + 0,3 H(C))`

Se P non è determinabile, score non calcolabile. `P=0, C=0` solo con assenza verificata, non con errore di accesso. Misura presenza e diversificazione osservate, **non** budget, ROAS o conversioni. Finestra e coefficienti provvisori.

### 2.5 Customer Satisfaction

nₖ = numero delle recensioni da k stelle (k=1..5); prior iniziale αₖ=1; N=Σnₖ, A=Σαₖ=5.

`S_REV = 25 × Σ_(k=1..5)[(k−1)(nₖ+αₖ)] / (N+A)`

Se solo media μ e numerosità N sono disponibili, possibile fallback **separato, esplicitamente marcato**:

`S_REV_fallback = 25 × [N(μ−1)+A(μ₀−1)] / (N+A)`

μ₀ è media di prior esplicita e A forza del prior; senza parametri non applicare il fallback. Il prior uniforme è provvisorio e tende verso 3 stelle; necessaria calibrazione. Conservare numero di recensioni, origine, limiti e incertezza.

### 2.6 Company Scale

R = fatturato annuo in **euro**; E = numero dipendenti. Entrambi riferiti alla società verificata e a date dichiarate.

`A_R = min(1, ln(1+R/1.000.000) / ln(101))`

`B_E = min(1, ln(1+E) / ln(1001))`

`S_SCALE = 50 × (A_R+B_E)`

Ancoraggi iniziali 100 M€ e 1.000 dipendenti, **provvisori** e configurabili per mercato prima della valutazione. In presenza di un solo campo, mostrare la singola componente come `Partial`, **non** attribuire all'altro il valore zero né calcolare lo score completo.

## 3. Indici complessivi: due formule fisse, non intercambiabili

Pesi di scenario iniziali, sperimentali:

| Dimensione | Peso |
|---|---:|
| POS | 20% |
| SEO | 25% |
| SOC | 15% |
| ADS | 10% |
| REV | 20% |
| SCALE | 10% |

**CCI₆:** `0,20 POS + 0,25 SEO + 0,15 SOC + 0,10 ADS + 0,20 REV + 0,10 SCALE`.

**CCI₄ (Core):** `(20 POS + 25 SEO + 20 REV + 10 SCALE) / 75`.

CCI₆ richiede tutte e sei le dimensioni `Valid`; CCI₄ richiede tutte e quattro le dimensioni Core `Valid`. Indici non calcolabili se mancano input essenziali. **Non** ricalcolare i pesi in base a ciò che è disponibile per *altri* competitor. **Non** confrontare CCI₄ e CCI₆ come se misurassero la stessa cosa.

## 4. Disponibilità, qualità e copertura

Ogni record: `score | status | coverage | uncertainty | source | timestamp | model_version`.

Stati: `Valid` (dati minimi verificati), `Partial` (metrica parziale ma non sufficiente per indice pieno), `Unavailable` (non calcolabile).

Soglie **iniziali da validare**, non scientificamente giustificate:

| Score | Valid (criterio pilota) | Esempio di Partial |
|---|---|---|
| POS | 4 criteri supportati da evidenze | Una o più evidenze insufficienti |
| SEO | >=95% della domanda ponderata con SERP verificate | Copertura inferiore alla soglia |
| SOC | >=10 post utilizzabili con periodo dichiarato | Meno di 10 post utilizzabili |
| ADS | 12 settimane effettivamente osservabili | Storico inferiore |
| REV | >=30 recensioni e copertura documentata | Campione ridotto / copertura incerta |
| SCALE | Entrambi i dati, esercizio <=3 anni | Un solo dato oppure informazioni non omogenee |

Queste soglie indicano completezza operativa del dataset, **non** certificazione della calibrazione matematica o della rappresentatività statistica.

## 5. Test numerico di regressione v1.1 (input fittizi)

| Dimensione | Input | Score atteso arrotondato |
|---|---|---:|
| POS | C=3, D=2, T=4, E=3 | 75,00 |
| SEO | V=[1200,600,300,100], p=[1,4,fuori top20 verificata,7], R=1 | 62,44 |
| SOC | ER=0,02, F=10000 | 50,00 |
| ADS | P=9/12, C=4 | 68,36 |
| REV | n₁…n₅=[2,3,5,20,70], αₖ=1 | 86,43 |
| SCALE | R=10.000.000€, E=100 | 59,38 |
| CCI₆ | Pesi come §3 | 68,17 |
| CCI₄ | Pesi Core come §3 | 71,78 |

Valori da calcolare sulle grandezze **non arrotondate**, confrontando l'output finale con tolleranza di arrotondamento appropriata.

## 6. Test e controlli obbligatori

1. Range `[0,100]` per tutti gli score validi.
2. Invarianza all'aggiunta/rimozione di competitor, con parametri e paniere invariati.
3. Monotonicità negli input per cui è prevista.
4. Dati mancanti ≠ zero; nessun CCI con dimensioni richieste non valide.
5. Test numerici della tabella §5.
6. SEO: p=1, p=20, p=21 e SERP fallita; paniere non-branded congelato.
7. Social: test esponenti −0,10/−0,15/−0,20, campioni insufficienti, F=0.
8. Ads: periodo di monitoraggio, deduplica creatività, assenza verificata vs fonte indisponibile.
9. Reviews: distribuzione 1–5, fallback esplicito, numero recensioni e prior.
10. Scale: un solo dato => `Partial`, nessun secondo input implicitamente zero.
11. Riproducibilità mediante snapshot, versioni dei parametri, rubriche, curve/trasformazioni e seed statistici.
12. Confronto delle rubriche AI con valutatori umani; controllo di accordo e variabilità.

### Sensitivity analysis

Perturbazione dei pesi via Dirichlet: `w_sim ~ Dirichlet(κ × w_base)`, κ iniziale 100, da variare nel test. Integrare anche l'incertezza degli score soltanto con modelli sostenuti dai dati. Frequenza del primo posto in simulazioni ≠ probabilità reale di superiorità.

## 7. Stato e condizioni di adozione

**Stato attuale:** formule specificate; alcuni esempi matematici presentati e riesaminati in conversazione, **nessun collaudo empirico end-to-end sul dataset del progetto**. Soglie e pesi sono provvisori.

**Prima dell'uso decisionale:** test con dati reali, QA delle fonti, calibrazione social/scale/ads, verifica affidabilità rubriche, analisi di saturazioni e sensibilità; correzioni mediante nuova versione, non modifiche silenziose ai parametri.

**Requisito di prodotto:** ciascun competitor ottiene una scorecard con le sei dimensioni; l'indice composto è mostrato **solo se calcolabile**, altrimenti indicare chiaramente perché manca.
