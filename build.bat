@echo off
chcp 65001 >nul
setlocal

if not exist ".\.venv\Scripts\activate.bat" (
    echo Virtual environment not found.
    echo Create it and install dependencies with:
    echo python -m venv .venv
    echo .\.venv\Scripts\activate
    echo pip install -r requirements.txt
    pause
    exit /b 1
)

call .\.venv\Scripts\activate.bat

python -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    echo PyInstaller is not installed in the virtual environment.
    echo Run:  pip install pyinstaller
    pause
    exit /b 1
)

echo Cleaning old build folders...
if exist build rmdir /s /q build
if exist dist  rmdir /s /q dist
if exist iFix.spec del /f /q iFix.spec

echo Building executable with PyInstaller...

python -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --windowed ^
  --onedir ^
  --name iFix ^
  --icon=logo.ico ^
  --paths=. ^
  --add-data "logo.ico;." ^
  --add-data "logo.png;." ^
  --add-data "data\ifix.db;data" ^
  --add-data "svg;svg" ^
  --hidden-import data.database ^
  --hidden-import pages.dashboard ^
  --hidden-import pages.vendas ^
  --hidden-import pages.clientes ^
  --hidden-import pages.tecnicos ^
  --hidden-import pages.garantia ^
  --hidden-import pages.laboratorio ^
  --hidden-import pages.catalogo ^
  --hidden-import pages.despesas ^
  --hidden-import pages.historicovendas ^
  --hidden-import pages.historicoentrega ^
  --hidden-import component.sidebar ^
  --hidden-import component.base_dialog ^
  --hidden-import component.svg_utils ^
  --hidden-import component.vizualizarcliente ^
  --hidden-import component.novocliente ^
  --hidden-import component.novotecnico ^
  --hidden-import component.novoproduto ^
  --hidden-import component.novocelular ^
  --hidden-import component.novavenda ^
  --hidden-import component.novaentrega ^
  --hidden-import component.novocancelamento ^
  --hidden-import component.novadespesa ^
  --hidden-import component.ordemdeservico ^
  --hidden-import component.notas ^
  --hidden-import component.whatsapp ^
  app.py

if errorlevel 1 (
    echo.
    echo Build failed.
    pause
    exit /b 1
)

echo.
echo Build complete. Check the folder: dist\iFix
pause
