@echo off
setlocal EnableDelayedExpansion
for /L %%i in (1,1,3) do (
  set "HEALTH_STATUS=ERR"
  for /f "tokens=2 delims= " %%j in ('curl -s -I http://localhost:9970/api/dashboard/health 2^>nul ^| findstr /b ""HTTP/""') do set "HEALTH_STATUS=%%j"
  echo Status: !HEALTH_STATUS!
)
