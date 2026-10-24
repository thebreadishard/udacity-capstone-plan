# Prints '<Win32_Battery BatteryStatus> <EstimatedChargeRemaining>' of the first battery, or nothing on a machine without one.
# Read by probes/watch.sh (check_power) and probes/state.sh; BatteryStatus 1 = discharging, 2 = on AC.
$battery = Get-CimInstance Win32_Battery | Select-Object -First 1
if ($battery) { '{0} {1}' -f $battery.BatteryStatus, $battery.EstimatedChargeRemaining }
