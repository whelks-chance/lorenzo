# The template FileZilla XML Queue input file (this is never changed)
$input = "FileZilla_Download_Queue.data"

# The version of the XML Queue input file to open with FileZilla
$output = "FileZilla_Download_Queue.xml"

# The placeholder to replace with the destination path
$search = "ABCDE"

echo "Looking for input file : $input"
$inputFileExists = Test-Path $input
if (-not $inputFileExists) {
  # echo "$input does not exist"
  echo -e "Input data file not found! Please run this file from the unzipped folder downloaded from the Bids website.\n\n"
  break
} else {
  echo "Building Filezilla download queue file.\n\n"
}
ß
# Get the user's Documents directory as the default destination
$documentFolderPath = [Environment]::GetFolderPath('MyDocuments')

# Repeatedly ask for the user's preferred destination (which can
# be the default by hitting return) until the destination exists
do {
  $usersPreferredDestinationPath = Read-Host -Prompt "Please enter the folder path to save files to [$documentFolderPath]"
  if (-not $usersPreferredDestinationPath) {
    $usersPreferredDestinationPath = $documentFolderPath
  }
  $usersPreferredDestinationPathExists = Test-Path $usersPreferredDestinationPath
  if (-not $usersPreferredDestinationPathExists) {
    echo "$usersPreferredDestinationPath does not exist, please either create it or choose another location.\n"

  }
} while (-not $usersPreferredDestinationPathExists)
$replace = $usersPreferredDestinationPath

echo "Building Filezilla download queue file.\n\n"


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

echo "Filezilla file created"
echo "To continue, run Filezilla, and select File -> Import and select the xml file in this folder.\n"
