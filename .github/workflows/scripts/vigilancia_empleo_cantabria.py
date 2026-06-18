#!/usr/bin/env python3
import datetime as dt
import html
import os
import re
import sys
import unicodedata
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from zoneinfo import ZoneInfo

TELEGRAM_LIMIT = 3900
CHAT_ID_ENV = "TELEGRAM_CHAT_ID"
TOKEN_ENV = "TELEGRAM_BOT_TOKEN"

FUENTES = [
    ("BOC Cantabria", "https://boc.cantabria.es/boces/"),
    ("Gobierno de Cantabria - Empleo publico", "https://www.cantabria.es/web/empleo-publico"),
    ("Gobierno de Cantabria - Convocatorias", "https://www.cantabria.es/web/empleo-publico/convocatorias"),
    ("SRE Cantabria - Convocatorias", "https://srecantabria.es/convocatorias/"),
    ("Ayuntamiento de Torrelavega", "https://www.torrelavega.es/"),
    ("Sede electronica Torrelavega", "https://sede.torrelavega.es/"),
]

PERFILES = [
    "tecnico superior en integracion social",
    "tecnico superior en educacion infantil",
    "tseis",
    "tsei",
    "integrador social",
    "integradora social",
    "educador infantil",
    "educadora infantil",
    "monitor de tiempo libre",
    "monitora de tiempo libre",
    "coordinador de tiempo libre",
    "coordinadora de tiempo libre",
    "conserje",
    "subalterno",
    "subalterna",
]

PROCESOS = [
    "convocatoria",
    "oposicion",
    "oposiciones",
    "bolsa",
    "bolsas",
    "sustitucion",
    "sustituciones",
    "proceso selectivo",
    "lista",
    "listas",
    "empleo publico",
    "contratacion",
    "estabilizacion",
    "plazo",
]

ABIERTAS = [
    "plazo abierto",
    "abierto el plazo",
    "presentacion de solicitudes",
    "admision de solicitudes",
    "solicitudes",
    "hasta el",
]


class LinkParser(HTMLParser):
    def __init__(self, base_url):
        super().__init__()
        self.base_url = base_url
        self.links = []
        self._href = None
        self._text = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "a":
            attrs = dict(attrs)
            href = attrs.get("href")
            if href:
                self._href = urllib.parse.urljoin(self.base_url, href)
                self._text = []

    def handle_data(self, data):
        if self._href:
            self._text.append(data)

    def handle_endtag(self, tag):
        if tag.lower() == "a" and self._href:
            title = clean(" ".join(self._text)) or self._href
            self.links.append((title, self._href))
            self._href = None
            self._text = []


def clean(text):
    return re.sub(r"\s+", " ", html.unescape(text or "")).strip()


def norm(text):
    text = clean(text)
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return text.lower()


def previous_month(today):
    first_this_month = today.replace(day=1)
    last_previous = first_this_month - dt.timedelta(days=1)
    first_previous = last_previous.replace(day=1)
    return first_previous, last_previous


def month_markers(start):
    meses = [
        "enero", "febrero", "marzo", "abril", "mayo", "junio",
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
    ]
    return [
        f"{start.month:02d}/{start.year}",
        f"{start.year}-{start.month:02d}",
        f"{meses[start.month - 1]} de {start.year}",
        f"{meses[start.month - 1]} {start.year}",
        str(start.year),
    ]


def fetch(url):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 empleo-publico-cantabria-monitor"},
    )
    with urllib.request.urlopen(req, timeout=25) as resp:
        raw = resp.read()
        ctype = resp.headers.get("content-type", "")
        match = re.search(r"charset=([\w-]+)", ctype)
        charset = match.group(1) if match else "utf-8"
        return raw.decode(charset, errors="replace")


def is_candidate(text, markers):
    n = norm(text)
    has_profile = any(term in n for term in PERFILES)
    has_process = any(term in n for term in PROCESOS)
    has_marker = any(norm(marker) in n for marker in markers)
    has_open = any(term in n for term in ABIERTAS)
    return has_profile and (has_process or has_marker or has_open), has_marker, has_open


def scan_source(name, url, markers):
    found = []
    try:
        body = fetch(url)
    except Exception as exc:
        return found, f"{name}: no se pudo revisar ({exc})"

    page_text = clean(re.sub(r"<[^>]+>", " ", body))
    ok, has_marker, has_open = is_candidate(page_text[:25000], markers)
    if ok:
        found.append({
            "fuente": name,
            "titulo": "Pagina principal con coincidencias",
            "url": url,
            "estado": "Convocatoria anterior aun abierta" if has_open and not has_marker else "Actuacion del periodo o candidata",
        })

    parser = LinkParser(url)
    parser.feed(body)
    seen = {item["url"] for item in found}

    for title, href in parser.links:
        ok, has_marker, has_open = is_candidate(f"{title} {href}", markers)
        if ok and href not in seen:
            found.append({
                "fuente": name,
                "titulo": title[:180],
                "url": href,
                "estado": "Convocatoria anterior aun abierta" if has_open and not has_marker else "Actuacion del periodo o candidata",
            })
            seen.add(href)

    return found, None


def build_report(results, errors, today, start, end):
    lines = [
        "Vigilancia de empleo publico en Cantabria",
        f"Fecha actual: {today.strftime('%d/%m/%Y')}",
        f"Periodo analizado: {start.strftime('%d/%m/%Y')} a {end.strftime('%d/%m/%Y')}",
        "",
    ]

    if results:
        lines.append("Resultados candidatos encontrados:")
        for i, item in enumerate(results, 1):
            lines += [
                "",
                f"{i}. {item['titulo']}",
                f"Organismo/fuente: {item['fuente']}",
                f"Estado: {item['estado']}",
                f"Enlace oficial: {item['url']}",
            ]
    else:
        lines.append("No se han encontrado resultados candidatos en las fuentes revisadas.")

    lines += ["", "Fuentes revisadas expresamente:"]
    for name, url in FUENTES:
        lines.append(f"- {name}: {url}")

    if errors:
        lines += ["", "Incidencias:"]
        lines += [f"- {err}" for err in errors]

    lines += [
        "",
        "Nota: abre siempre el enlace oficial para verificar bases, requisitos y plazos antes de presentar solicitud.",
    ]
    return "\n".join(lines)


def send_telegram(text):
    token = os.environ.get(TOKEN_ENV)
    chat_id = os.environ.get(CHAT_ID_ENV)
    if not token or not chat_id:
        raise RuntimeError("Faltan TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID en GitHub Secrets.")

    endpoint = f"https://api.telegram.org/bot{token}/sendMessage"
    chunks = []
    rest = text
    while len(rest) > TELEGRAM_LIMIT:
        cut = rest.rfind("\n", 0, TELEGRAM_LIMIT)
        if cut < 1000:
            cut = TELEGRAM_LIMIT
        chunks.append(rest[:cut].strip())
        rest = rest[cut:].strip()
    if rest:
        chunks.append(rest)

    for chunk in chunks:
        data = urllib.parse.urlencode({
            "chat_id": chat_id,
            "text": chunk,
            "disable_web_page_preview": "true",
        }).encode("utf-8")
        req = urllib.request.Request(endpoint, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=25) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            if '"ok":true' not in body:
                raise RuntimeError(f"Telegram no confirmo el envio: {body[:300]}")


def main():
    today = dt.datetime.now(ZoneInfo("Europe/Madrid")).date()
    start, end = previous_month(today)
    markers = month_markers(start)

    results = []
    errors = []
    for name, url in FUENTES:
        found, error = scan_source(name, url, markers)
        results.extend(found)
        if error:
            errors.append(error)

    report = build_report(results, errors, today, start, end)
    print(report)
    send_telegram(report)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
