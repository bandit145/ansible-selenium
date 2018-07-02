param(
    [string]$AnsibleSeleniumPath
)

$env:ansible_selenium_path = $AnsibleSeleniumPath

vagrant up --provision