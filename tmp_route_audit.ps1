$ErrorActionPreference='SilentlyContinue'
$base='https://clisonix.com'
$root='c:\Users\Admin\Desktop\Clisonix-cloud\apps\web\app'
$moduleDirs=Get-ChildItem "$root\modules" -Directory | Where-Object { Test-Path (Join-Path $_.FullName 'page.tsx') }
$moduleUrls=@('/modules') + ($moduleDirs | ForEach-Object { '/modules/' + $_.Name })
$apiFiles=Get-ChildItem "$root\api" -Recurse -Filter route.ts | ForEach-Object {
  $rel=$_.FullName.Substring((Join-Path $root 'api').Length).TrimStart('\\')
  $rel=$rel -replace '\\route\.ts$',''
  if($rel -match '\\['){ return }
  '/api/' + ($rel -replace '\\','/')
}
$apiUrls=$apiFiles | Sort-Object -Unique
$okCodes=@(200,201,202,204,301,302,307,308,400,401,403,405)
$results=@()
foreach($u in $moduleUrls){
  try{ $r=Invoke-WebRequest -UseBasicParsing -Uri ($base+$u) -Method GET -MaximumRedirection 2 -TimeoutSec 12; $c=[int]$r.StatusCode }
  catch { $c = if($_.Exception.Response){ [int]$_.Exception.Response.StatusCode.value__ } else { 0 } }
  $results += [pscustomobject]@{kind='module';url=$u;code=$c}
}
foreach($u in $apiUrls){
  try{ $r=Invoke-WebRequest -UseBasicParsing -Uri ($base+$u) -Method GET -MaximumRedirection 1 -TimeoutSec 10; $c=[int]$r.StatusCode }
  catch { $c = if($_.Exception.Response){ [int]$_.Exception.Response.StatusCode.value__ } else { 0 } }
  $results += [pscustomobject]@{kind='api';url=$u;code=$c}
}
$bad=$results | Where-Object { $okCodes -notcontains $_.code } | Sort-Object kind,url
$out=@()
$out += "TOTAL_MODULES=$($moduleUrls.Count) TOTAL_API=$($apiUrls.Count) BAD=$($bad.Count)"
$out += ($bad | ForEach-Object { "$($_.kind) $($_.code) $($_.url)" })
$out | Set-Content -Path 'c:\Users\Admin\Desktop\Clisonix-cloud\route_audit.txt' -Encoding UTF8
Get-Content 'c:\Users\Admin\Desktop\Clisonix-cloud\route_audit.txt' -TotalCount 120
