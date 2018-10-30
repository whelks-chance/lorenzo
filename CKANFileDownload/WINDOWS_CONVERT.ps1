# The template FileZilla XML Queue input file (this is never changed)
$input = "FileZilla_Download_Queue.xml"

# The version of the XML Queue input file to open with FileZilla
$output = "FileZilla_Download_Queue-new.xml"

# The placeholder to replace with the destination path
$search = "ABCDE"

# Get the user's Documents directory as the default destination
$documentFolderPath = [Environment]::GetFolderPath('MyDocuments')

# Repeatedly ask for the user's preferred destination (which can
# be the default by hitting return) until the destination exists
do {
  $usersPreferredDestinationPath = Read-Host -Prompt "Enter the destination folder [$documentFolderPath]"
  if (-not $usersPreferredDestinationPath) {
    $usersPreferredDestinationPath = $documentFolderPath
  }
  $usersPreferredDestinationPathExists = Test-Path $usersPreferredDestinationPath
  if (-not $usersPreferredDestinationPathExists) {
    echo "$usersPreferredDestinationPath does not exist"
  }
} while (-not $usersPreferredDestinationPathExists)
$replace = $usersPreferredDestinationPath

# Read the content of the FileZilla XML Queue file
$content = Get-Content $input

# Replace the placeholder with the destination path
$content = $content -replace $search, $replace

# Replace the UNIX forward slashes with Windows back slashes
$content = $content -replace '/', '\'

# Fix the closing XML tags affected by the forward to back slash replacement
# e.g. </File> -> <\File> -> </File>
$content = $content -replace '\<\\', '</'

# Save the processed output file
Out-File -FilePath $output -InputObject $content
