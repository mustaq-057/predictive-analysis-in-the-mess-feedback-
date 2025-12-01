# This script starts the Mess App server and fixes any port issues
Write-Host "Starting Mess App..."

# We want to run the app on port 3005
$port = 3005

# Check if something is already running on this port
$tcp = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue

if ($tcp) {
    Write-Host "Port $port is in use. Killing old process..."
    # Get the ID of the old process
    $procId = $tcp.OwningProcess
    # Force kill the old process
    Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
    Write-Host "Killed process $procId"
}

# Start the Next.js development server
Write-Host "Starting server on http://localhost:3005"
npm run dev
