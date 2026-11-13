@echo off
cd /d "%~dp0"
where python >nul 2>nul && (python serveur.py & goto :eof)
where py >nul 2>nul && (py serveur.py & goto :eof)
echo Python n est pas installe. Installe-le depuis python.org puis relance ce fichier.
pause
