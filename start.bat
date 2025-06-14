@echo off
echo ========================================
echo  Motion Tracking Music Generator
echo ========================================
echo.

echo [1/3] Pornesc Max/MSP cu patch-ul principal...
start "" "./src/imeciss.maxpat"

echo [2/3] Astept 10 secunde pentru incarcarea Max/MSP...
timeout /t 10 /nobreak

echo [3/3] Pornesc scriptul Python pentru tracking...
echo.
echo INSTRUCTIUNI:
echo - Pozitioneaza-te la 1-2 metri de camera
echo - Asigura-te ca fata si mainile sunt vizibile
echo - Tine ochii inchisi 0.75 secunde pentru toggle
echo - Apasa Ctrl+C pentru a opri
echo.
echo ========================================

python ./src/tracker.py

echo.
echo Script terminat. Apasa orice tasta pentru a inchide...
pause >nul