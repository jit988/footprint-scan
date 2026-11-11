# OSINT Toolkit

Runs holehe, h8mail, PhoneInfoga, Sherlock and Maigret from one command and
saves everything under `results/<timestamp>/`.

## Kali / Debian / Ubuntu
    chmod +x setup.sh run.sh
    ./setup.sh
    ./run.sh --authorized --email you@example.com

## Termux (Android)
    pkg install -y git
    git clone <your-repo-url> osint-toolkit && cd osint-toolkit
    chmod +x setup.sh run.sh
    ./setup.sh          # slow the first time: lxml and others compile on-device
    ./run.sh --authorized --username yourhandle
Tip: run `termux-wake-lock` so Android doesn't kill the install.

## Docker
    docker compose build
    docker compose run --rm osint --authorized --email you@example.com
    # results appear in ./results on your host
(Without compose: `docker build -t osint-toolkit .` then
`docker run --rm -v "$PWD/results:/app/results" osint-toolkit --authorized --username x`)

## Options
    --email  --phone +919876543210  --username  --name "Full Name"
    --timeout 300    --authorized (required)

## Lawful use only
Use only on your own data, or with written permission / a lawful basis
(pentest scope, due diligence). Do not use it to stalk, harass or impersonate
anyone. Compiled personal data may be covered by GDPR, India's DPDP Act, etc.
Results are leads, not proof. Never commit `results/`.
