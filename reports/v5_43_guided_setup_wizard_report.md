# V5.43 Guided Local Setup Wizard Report

- likely blocker: Node.js is not installed or not available in PATH
- recommended next step: Install Node.js LTS manually, reopen the terminal, then run node -v.
- missing requirements: node_available, npm_available, frontend_node_modules_exists, frontend_port_3000_open, backend_port_8000_open

## Mac Steps

- Open terminal: Open Terminal on Mac or PowerShell on Windows.
- Enter project directory: Go to the shandong project folder.
- Check Python: Confirm Python can run local scripts.
- Install Node.js LTS manually: Install Node.js LTS if Node is missing.
- Reopen terminal: Close and reopen your terminal after installing Node.js.
- Check Node and npm: Confirm Node and npm are available.
- Install pnpm manually: Install pnpm using npm.
- Install frontend dependencies: Install frontend packages.
- Start backend: Start the local API server.
- Start frontend: Start the local web server.
- Open browser: Open the product home page.
- Verify Product Home Dashboard: Confirm the Shandong Quant System home page loads.

## Windows Steps

- Open terminal: Open Terminal on Mac or PowerShell on Windows.
- Enter project directory: Go to the shandong project folder.
- Check Python: Confirm Python can run local scripts.
- Install Node.js LTS manually: Install Node.js LTS if Node is missing.
- Reopen terminal: Close and reopen your terminal after installing Node.js.
- Check Node and npm: Confirm Node and npm are available.
- Install pnpm manually: Install pnpm using npm.
- Install frontend dependencies: Install frontend packages.
- Start backend: Start the local API server.
- Start frontend: Start the local web server.
- Open browser: Open the product home page.
- Verify Product Home Dashboard: Confirm the Shandong Quant System home page loads.

## Command Blocks

- Mac setup commands: cd path/to/shandong && python scripts/run_v542_local_run_doctor.py && node -v && npm -v && npm install -g pnpm && cd web/frontend && pnpm install && pnpm dev --hostname 127.0.0.1 --port 3000
- Mac backend terminal: python -m uvicorn src.api.v2.server:create_v2_api_app --factory --host 127.0.0.1 --port 8000
- Windows setup commands: cd path\to\shandong && python scripts\run_v542_local_run_doctor.py && node -v && npm -v && npm install -g pnpm && cd web\frontend && pnpm install && pnpm dev --hostname 127.0.0.1 --port 3000
- Windows backend PowerShell: python -m uvicorn src.api.v2.server:create_v2_api_app --factory --host 127.0.0.1 --port 8000

## Plain Language Explanation

- 3000 is the frontend web page service.
- If 127.0.0.1:3000 does not open, the frontend is usually not running.
- Current likely blocker: Node.js is not installed or not available in PATH
- 3000 is the frontend page you open in the browser.
- 8000 is the backend API service used by the frontend.
- Python backend passing TestClient means the code is valid, but it does not mean the browser page has started.
- Node.js is the tool needed to run the web frontend.
- pnpm is the tool that installs and runs frontend dependencies.
- Install Node.js LTS manually, reopen the terminal, then run node -v.

## Safety Boundary

- Current stage is guided setup wizard only.
- It does not automatically install dependencies.
- It does not automatically access external networks.
- It does not connect to a real broker.
- It does not connect to a sandbox API.
- It does not read secrets.
- It does not read accounts, balances, or positions.
- It does not submit orders.
- It does not connect to real money.
