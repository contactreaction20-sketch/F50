$secureKey = Read-Host "Enter your NEW NVIDIA API key" -AsSecureString
$pointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureKey)
try {
    $env:F50_MODEL_API_KEY = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer)
} finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer)
}
$env:F50_MODEL_API_URL = "https://integrate.api.nvidia.com/v1"
$env:F50_MODEL_NAME = "google/gemma-4-31b-it"
python -m future50 --chat --host 127.0.0.1 --port 8765
