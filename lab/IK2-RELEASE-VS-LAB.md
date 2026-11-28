# maya-ik2 : la release v1.1.84 contre la branche lab (28/11/2026)

Cette branche est le tag **v1.1.84** plus nos PR Inkling 2 encore ouvertes, dans l'ordre où elles y sont posées :

| Commit | PR | Ce qu'il ajoute |
|---|---|---|
| `d7870731` | [#1256](https://github.com/mw00/project-maya/pull/1256) | deux cartes : la paire sans P2P prend le transit le plus court, mesuré au chargement (`MAYA_LINK_PICK`) |
| `af974c54` | [#1332](https://github.com/mw00/project-maya/pull/1332) | lit les GGUF écrits comme llama.cpp master les écrit (`inkling2_loop`) : les fichiers d'unsloth depuis le 23/11 |
| `b66b7f1f` | [#1344](https://github.com/mw00/project-maya/pull/1344) | le chemin résident là où les projections ne sont pas fusionnées (`IK2_RESIDENT_UNFUSED=1`, off par défaut) |
| `1da4129c`, `2366cf39` | [#1330](https://github.com/mw00/project-maya/pull/1330) | un drafteur DFlash2 |

Refaire la mesure : compiler le tag et la branche avec la même chaîne, puis

    python lab/ik2_release_vs_lab.py --release <maya-ik2 du tag v1.1.84> --lab <maya-ik2 de cette branche> --stop-task "\llama-swap"

Les moteurs sont sur la ligne de commande, gloutons, cache KV en FP8, avec le profil d'experts (`IK2_WARM`), 512 jetons sur
`lab/ids302.txt` (302 jetons) ; deux courses par bras, entrelacées ; les jetons générés sont comparés (colonne « Jetons » :
« idem » = identiques à ceux du premier bras du cas).

## Résultats (RTX 5080 16 Go + RTX 4060 Ti 16 Go, Windows 11, 31 Go de RAM)

| Cas | Bras | t/s (médiane de 2 courses) | Jetons |
|---|---|---|---|
| Q4_K_XL - RTX 5080 - sans draft | release | **49.8** (50.1 / 49.5) | idem |
| Q4_K_XL - RTX 5080 - sans draft | lab | **50.5** (50.3 / 50.7) | idem |
| Q4_K_XL - RTX 4060 Ti - sans draft | release | **30.1** (27.4 / 32.7) | idem |
| Q4_K_XL - RTX 4060 Ti - sans draft | lab | **30.4** (28.2 / 32.5) | idem |
| Q4_K_XL - deux cartes - sans draft | release | **68.1** (68.3 / 68.0) | idem |
| Q4_K_XL - deux cartes - sans draft | release + anneau | **82.2** (81.6 / 82.8) | idem |
| Q4_K_XL - deux cartes - sans draft | lab | **72.7** (73.1 / 72.3) | idem |
| Q4_K_XL - deux cartes - sans draft | lab + anneau | **83.8** (84.3 / 83.3) | idem |
| Q4_K_XL - RTX 5080 - DSpark (ctx 32K) | release | **66.7** (65.6 / 67.8) | idem |
| Q4_K_XL - RTX 5080 - DSpark (ctx 32K) | lab | **68.1** (67.8 / 68.4) | idem |
| Q4_K_XL - RTX 4060 Ti - DSpark (ctx 32K) | release | **10.0** (9.9 / 10.1) | idem |
| Q4_K_XL - RTX 4060 Ti - DSpark (ctx 32K) | lab | **10.1** (10.1 / 10.1) | idem |
| Q4_K_XL - deux cartes - DSpark (ctx 32K) | release | **132.3** (134.9 / 129.7) | idem |
| Q4_K_XL - deux cartes - DSpark (ctx 32K) | release + anneau | **170.1** (170.1 / 170.1) | idem |
| Q4_K_XL - deux cartes - DSpark (ctx 32K) | lab | **136.4** (137.4 / 135.4) | idem |
| Q4_K_XL - deux cartes - DSpark (ctx 32K) | lab + anneau | **170.4** (170.5 / 170.4) | idem |
| Q4_K_XL - deux cartes - DFlash2 (ctx 32K, anneau) | lab + anneau | **82.4** (82.8 / 82.1) | idem |
| Q4_K_XL - deux cartes - DFlash2 (ctx 32K, anneau) | lab + anneau + DFlash2 (6) | **167.9** (163.7 / 172.1) | autres |
| Q4_K_XL - deux cartes - DFlash2 (ctx 32K, anneau) | lab + anneau + DFlash2 (4) | **146.7** (146.1 / 147.4) | autres |
| IQ3_XXS - RTX 5080 - sans draft | release | **64.6** (64.7 / 64.5) | idem |
| IQ3_XXS - RTX 5080 - sans draft | lab | **65.3** (65.2 / 65.3) | idem |
| IQ3_XXS - RTX 5080 - sans draft | lab + résident | **120.2** (120.2 / 120.1) | autres |
| IQ3_XXS - RTX 5080 - sans draft | lab + résident, fichier du 23/11 | **117.9** (117.2 / 118.7) | autres |
| IQ3_XXS - RTX 4060 Ti - sans draft | release | **43.4** (43.5 / 43.2) | idem |
| IQ3_XXS - RTX 4060 Ti - sans draft | lab | **43.4** (43.3 / 43.5) | idem |
| IQ3_XXS - RTX 4060 Ti - sans draft | lab + résident | **58.2** (58.2 / 58.2) | autres |
| IQ3_XXS - RTX 4060 Ti - sans draft | lab + résident, fichier du 23/11 | **57.9** (58.0 / 57.9) | autres |
| IQ3_XXS - RTX 5080 - DSpark (ctx 16K) | release | **48.6** (47.8 / 49.3) | idem |
| IQ3_XXS - RTX 5080 - DSpark (ctx 16K) | lab + résident | **167.4** (167.4 / 167.4) | autres |
| IQ3_XXS - RTX 4060 Ti - DSpark (ctx 16K) | release | **23.5** (23.4 / 23.6) | idem |
| IQ3_XXS - RTX 4060 Ti - DSpark (ctx 16K) | lab + résident | **76.0** (76.0 / 76.1) | autres |
| IQ3_XXS - deux cartes - DSpark (ctx 16K) | release | **48.2** (47.9 / 48.5) | idem |
| IQ3_XXS - deux cartes - DSpark (ctx 16K) | lab + résident | **171.3** (172.4 / 170.2) | autres |
| IQ3_XXS (fichier actuel) - RTX 5080 - draft (ctx 16K) | lab + résident, fichier du 23/11 | **164.3** (162.2 / 166.3) | idem |
| IQ3_XXS (fichier actuel) - RTX 5080 - draft (ctx 16K) | lab + résident + DFlash2 (4) | **160.5** (159.5 / 161.6) | autres |
| IQ3_XXS (fichier actuel) - RTX 5080 - draft (ctx 16K) | lab + résident + DFlash2 (6) | **173.8** (173.1 / 174.5) | autres |

## Lecture

- **Sans réglage, la branche lab est la release** : mêmes jetons sur chaque cas (Q4 et IQ3, les deux cartes et les deux
  monos), même vitesse à ±1 %.
- **#1256 (deux cartes)** : 68 → 73 t/s sans draft, 132 → 136 avec DSpark ; les jetons sont ceux de la release.
- **L'anneau** (`IK2_PEER_DIRECT_SIGNAL=1`, déjà dans la release depuis v1.1.83, éteint par défaut) : 68 → 82 sans draft,
  132 → 170 avec DSpark. Avec l'anneau, lab et release sont égales.
- **#1344 (IQ3, une carte)** : 65 → 120 t/s sur la 5080, 43 → 58 sur la 4060 Ti ; avec DSpark (contexte 16K, où le
  drafteur tient) 49 → 167 et 24 → 76. Les jetons changent là où deux candidats sont à quasi-égalité (PR #1344).
- **#1332** : le fichier d'unsloth d'aujourd'hui tourne comme l'ancien (118 contre 120 t/s) ; la release le refuse.
- **#1330 (DFlash2)** : en deux cartes 168 t/s à la fenêtre 6, contre 170 pour DSpark ; sur le IQ3 en résident 174
  contre 167.
- **Le IQ3 n'utilise pas la deuxième carte** dans Maya (« GPU 0 holds every expert ») : le cas « deux cartes » vaut le mono.
- **Q4 + DSpark sur la 4060 Ti tombe à 10 t/s** (30 sans draft), release comme lab : la carte affiche le bureau et le
  drafteur prend la place des experts ; pas creusé.

## Les drafters sur du vrai texte (28/11, après lecture de simplexai-labs/PolyStrata#339)

Le prompt de ce banc (`lab/ids302.txt`) est une liste répétitive (« Entry 1: at the market hall… ») : les suppositions y
sont gardées à 85-99 %, par le prompt lookup comme par les drafters eux-mêmes (88-93 % lookup coupé). Les barres
« + DSpark / DFlash2 » ci-dessus comparent donc les chemins spéculatifs des moteurs sur un terrain facile, pas le draft
sur du texte ordinaire. Refait comme le demande cette issue : prompt lookup coupé (`--lookup 0`, `IK2_LOOKUP=0`), deux
prompts réels (code, 175 jetons ; récit, 145 jetons), 256 jetons, fenêtres 4 / 6 / 8, deux courses par case, la meilleure
fenêtre gardée. t/s, et la part des suppositions gardées.

| Carte, prompt | PolyStrata sans draft | + DSpark | + DFlash2 Q8_0 | Maya sans draft | + DSpark | + DFlash2 |
|---|---|---|---|---|---|---|
| RTX 5080, code | 154 | 234 (w6, 75 %) | 228 (w8, 77 %) | 119 | 142 (w6, 72 %) | 141 (w4, 78 %) |
| RTX 5080, récit | 153 | 174 (w4, 46 %) | 190 (w8, 69 %) | 119 | 110 (w6, 17 %) | 119 (w4, 56 %) |
| RTX 4060 Ti, code | 65 | 109 (w8, 76 %) | 105 (w8, 79 %) | 59 | 67 (w6, 72 %) | 60 (w4, 63 %) |
| RTX 4060 Ti, récit | 64 | 76 (w4, 46 %) | 83 (w8, 69 %) | 59 | 55 (w4, 22 %) | 56 (w6, 52 %) |

PolyStrata : branche `feat/inkling2-dflash2` (dc5468a08). Maya : cette branche (chemin résident, contexte 16K).

- Sur du code, les deux drafters se valent à la fenêtre 4 (PolyStrata 5080 : 216 contre 211) ; DSpark garde l'avance sur
  PolyStrata aux fenêtres larges (234 contre 215 à 6), DFlash2 rattrape à 8 (228).
- Sur le récit, DFlash2 profite de la fenêtre (PolyStrata 5080 : 171, 173, 190) quand DSpark recule (174, 170, 164).
- Chez Maya, le draft ne gagne que sur du code (+19 % sur la 5080, +14 % sur la 4060 Ti) et rien sur le récit (110-119
  contre 119 sans draft) : la vérification d'une fenêtre y coûte ce que les suppositions rapportent.

## Les réglages qui comptent en mono (balayage du 28/11)

| Fichier, cas | Réglage | Effet |
|---|---|---|
| IQ3, une carte | `IK2_RESIDENT_UNFUSED=1` (cette branche) | ×1,8 sur la 5080, ×1,3 sur la 4060 Ti |
| Q4, une carte, sans draft | `IK2_LANE=cpu` (dans la release, off) | **+22 à 28 %** (50 → 61-65 t/s sur la 5080) : les experts qui ne tiennent pas en VRAM sont calculés par le processeur (4 fils, le défaut) au lieu d'arriver par PCIe |
| Q4, une carte, avec DSpark | `IK2_LANE=cpu` | −4 % (ne pas l'activer) |
| deux cartes | `IK2_PEER_DIRECT_SIGNAL=1` (release, off) | +21 % sans draft, +29 % avec |

Balayés sans gain sur le IQ3 (chemin résident, ±1 %) : `IK2_ATTN_MMA=0` (−4 %) et `2` (−3 %), `IK2_ROWS_R=2`/`4`,
`IK2_Q6_COLS=0`, `IK2_EXPERT_MMA=0`, `IK2_CAND=0` ; avec DSpark (le bruit des courses de référence va de 162 à 182 t/s) :
`IK2_DRAFT_WIDTH=4`/`6`, `IK2_DRAFT_ADAPT=0` (seul `ADAPT=0 + WIDTH=6` sort un peu : 187 sur deux courses).
Deux réglages arrêtent le moteur ici : `IK2_CPU=1` (`cudaHostAlloc … out of memory`, ik2_main.cu) et, avec
`IK2_RESIDENT_UNFUSED=1`, `IK2_BLOCK_EXACT=0` (« the block path: a dense matrix that is not planar Q8_0 »).
`IK2_COLS_AHEAD=0`, `IK2_ATTN_TOKS=0` et `IK2_BLOCK=0` perdent (−7 %, −11 %, −70 %).

## D'où vient l'écart qui reste avec PolyStrata en mono

IQ3_XXS, RTX 5080, sans draft : Maya 120 t/s, PolyStrata 152-154 ; avec DSpark (fenêtre 4) Maya 167-173 contre
PolyStrata 234-235 (binaire de prod du 25/11, 512 jetons) et 277-302 (build du main 42e489d14 du 27/11 ; 302 sur une
génération de 1 600 jetons).

- **Pendant le décodage la carte est occupée à 99 % par les deux moteurs** (un noyau tourne presque tout le temps). L'écart
  est dans la lecture des poids : mémoire active 67 % du temps avec Maya contre 72 % avec PolyStrata ; avec un draft,
  52 % contre 68 %.
- **Traçage de chaque noyau** (CUPTI lié au moteur, `IK2_GRAPH=0` pour que Maya lance ses noyaux un par un) : Maya lance
  **868 noyaux par jeton**, 18 par visite de couche. 565 d'entre eux durent moins de 7 µs et prennent 27 % du temps ;
  les projections d'attention 39 % (dont 27 lancements du noyau à points-lignes d'une matrice non Q8, à 40 µs pièce,
  quatre fois le temps du noyau Q8 planaire sur une matrice de même taille) ; les experts 39 % ; normes, résidus et portes 13 %.
  PolyStrata lance **environ 6 noyaux par jeton** : un noyau persistant (`ink_mix_kernel`, 1 024 fils) fait toute la
  couche en 5,6 ms ; avec une fenêtre de 4 jetons le même noyau met 10 ms, soit 1,8 fois le prix d'un jeton.
- Ce n'est donc pas un réglage : c'est la forme du moteur (des dizaines de petits noyaux par couche contre un noyau
  fusionné). Côté Maya, deux pistes chiffrables : convertir à la charge les matrices Q6_K en Q8 planaire (exact pour
  Q6_K ; près de 0,9 ms par jeton sur 8,6) et fusionner les petits noyaux.
- **Sur le Q4 en mono**, Maya garde 2 235 experts sur 3 072 en VRAM et lit les autres par PCIe (15 % des tirages) :
  mémoire active 29 %, 50 t/s. PolyStrata calcule les siens sur le processeur (charge processeur 70 %).

Une réserve sur PolyStrata et le Q4 : 121 t/s le 25/11 (binaire de prod), 76 à 85 t/s le 28/11 avec le même binaire et
la même commande (« router wait » 0,1 puis 4,3 ms par jeton). Ni le build (trois binaires comparés), ni la résolution du
minuteur Windows ; cause non trouvée.
