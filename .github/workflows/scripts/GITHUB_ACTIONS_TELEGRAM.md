# Vigilancia diaria por GitHub Actions

Este repositorio ejecuta una vigilancia diaria de empleo publico en Cantabria y envia el informe a Telegram.

## Secretos necesarios

En GitHub, entra en:

`Settings > Secrets and variables > Actions > New repository secret`

Crea estos dos secretos:

- `TELEGRAM_BOT_TOKEN`: el token nuevo del bot, sin la palabra `bot`.
- `TELEGRAM_CHAT_ID`: `937405384`

## Ejecucion

El workflow esta en:

`.github/workflows/vigilancia-empleo-cantabria.yml`

Se ejecuta:

- automaticamente cada dia a las 10:00, zona horaria `Europe/Madrid`
- manualmente desde la pestana `Actions`, usando `Run workflow`

## Archivos principales

- `scripts/vigilancia_empleo_cantabria.py`: revisa las fuentes oficiales y envia el informe.
- `.github/workflows/vigilancia-empleo-cantabria.yml`: programa la ejecucion en GitHub Actions.

## Nota

El script marca resultados candidatos encontrados en fuentes oficiales. Antes de presentar una solicitud, abre siempre el enlace oficial y verifica bases, requisitos y plazos.
