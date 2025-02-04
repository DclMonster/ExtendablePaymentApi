# Build both Python and TypeScript documentation

Write-Host "Building Python (Sphinx) Documentation..." -ForegroundColor Green

# Setup Python virtual environment
python -m venv docs_venv
./docs_venv/Scripts/Activate.ps1

# Install Python documentation requirements
pip install -r py_payment_api/docs/requirements.txt

# Build Sphinx docs
Set-Location py_payment_api/docs
sphinx-build -b html . _build/html
Set-Location ../..

Write-Host "Python documentation built successfully!" -ForegroundColor Green
Write-Host "View at: py_payment_api/docs/_build/html/index.html" -ForegroundColor Yellow

Write-Host "`nBuilding TypeScript (TypeDoc) Documentation..." -ForegroundColor Green

# Install npm packages and build TypeDoc
Set-Location tsPaymentApi
npm install
npm run docs

Write-Host "TypeScript documentation built successfully!" -ForegroundColor Green
Write-Host "View at: tsPaymentApi/docs/index.html" -ForegroundColor Yellow

# Deactivate Python virtual environment
deactivate 