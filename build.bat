@echo off
if not exist ".\.venv\Scripts\activate.bat" (
    echo "Virtual environment not found! Please create it and run: pip install -r requirements.txt"
    pause
    exit /b 1
)

call .\.venv\Scripts\activate.bat

echo "Building executable with PyInstaller..."
pyinstaller ^
  --noconfirm ^
  --clean ^
  --windowed ^
  --onedir ^
  --name iFix ^
  --icon=logo.ico ^
  --add-data "logo.png;." ^
  --add-data "data\ifix.db;data" ^
  --hidden-import pages.dashboard ^
  --hidden-import pages.vendas ^
  --hidden-import pages.clientes ^
  --hidden-import pages.tecnicos ^
  --hidden-import pages.garantia ^
  --hidden-import pages.laboratorio ^
  --hidden-import pages.catalogo ^
  --hidden-import component.sidebar ^
  --hidden-import component.vizualizarcliente ^
  --hidden-import component.ordemdeserviço ^
  --hidden-import component.novavenda ^
  --hidden-import component.novocliente ^
  --hidden-import component.novotecnico ^
  --hidden-import component.notas ^
  app.py

echo "Build complete. Check the 'dist/iFix' folder."
pause
