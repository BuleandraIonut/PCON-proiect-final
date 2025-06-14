# Motion Tracking Music Generator

Un sistem interactiv de muzica generativa care transforma miscarile corpului in sunet folosind camera web. Controleaza muzica prin miscarea capului, ochilor si mainilor in timp real.

## Arhitectura Sistemului

### Diagrama Generala
![Arhitectura Generala](General_Architecture.png)

### Fluxul Scriptului Python
![Fluxul Tracker-ului](tracker_SWDD.png)

## Instalare

### Cerinte
- Python
- Max/MSP
- Camera web
- Boxe/casti

### Setup Python
```bash
pip install mediapipe opencv-python python-osc
```

### Fisiere Audio
Pune fisierele WAV in folderul proiectului:
- `A4.wav`, `C4.wav`, `D4.wav`, `E4.wav`, `F4.wav`, `G4.wav`
- `VA4.wav`, `VC4.wav`, `VD4.wav`, `VE4.wav`, `VF4.wav`, `VG4.wav`

### Pornire Automata
Foloseste `start.bat` pentru pornire automata - deschide Max/MSP, asteapta 10 secunde, apoi porneste tracking-ul.

## Utilizare

### Pornire Manuala
1. Deschide Max/MSP si patch-ul `imeciss.maxpat`
2. Ruleaza scriptul Python:
   ```bash
   python tracker.py
   ```
3. Pozitioneaza-te la 1-2 metri de camera

### Controluri
- **Cap**: Miscarea pe X controleaza ritmul, pe Y controleaza melodia
- **Ochi**: Tine ochii inchisi 0.75 secunde pentru toggle on/off
- **Maini**: Pozitia controleaza instrumentele, inchis/deschis = pornit/oprit

### Comunicatie
Scriptul trimite coordonate via OSC pe portul 8999 catre Max/MSP:
- `/cap [x, y, z]` - pozitia capului
- `/ochi [0/1]` - starea ochilor
- `/manaStanga [x, y, z]` - pozitia mainii stangi
- `/manaStangaInchisa [0/1]` - starea mainii stangi
- `/manaDreapta [x, y, z]` - pozitia mainii drepte
- `/manaDreaptaInchisa [0/1]` - starea mainii drepte

## Istoric


## Link-uri

