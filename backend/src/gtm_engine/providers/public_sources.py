"""Bounded anonymous access and normalization for Gate 1E public sources."""

import io
import json
import math
import re
import xml.etree.ElementTree as ET
import zipfile
from itertools import product

import httpx

MAX_BYTES = 10_000_000
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
ATECO_URL = "https://www.istat.it/wp-content/uploads/2025/02/StrutturaATECO-2025-IT-EN-DE.xlsx"
SAMPLES = {
    "istat_ateco": (ATECO_URL, {}),
    "eurostat": (
        "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/DEMO_R_D3DENS",
        {"lang": "EN", "geo": "ITC11", "time": "2023"}),
    "esco": ("https://ec.europa.eu/esco/api/search",
             {"text": "event", "type": "occupation", "language": "en", "limit": "5",
              "selectedVersion": "v1.2.0"}),
    "openalex": ("https://api.openalex.org/works",
                 {"search": "team building", "per_page": "3",
                  "select": "id,title,doi,publication_year,type"}),
}


class PublicSourceError(Exception):
    """Fixed codes only: never forward remote error text."""


def download(client: httpx.Client, source: str) -> tuple[bytes, dict]:
    url, params = SAMPLES[source]
    with client.stream("GET", url, params=params) as response:
        meta = {"status_code": response.status_code,
                "content_type": response.headers.get("content-type"),
                "redirect_location": response.headers.get("location"),
                "etag": response.headers.get("etag"),
                "last_modified": response.headers.get("last-modified")}
        if response.status_code != 200:
            return b"", meta
        body = bytearray()
        for chunk in response.iter_bytes():
            body.extend(chunk)
            if len(body) > MAX_BYTES:
                raise PublicSourceError("response_too_large")
        return bytes(body), meta


def ateco_rows(body: bytes) -> list[dict]:
    """Read only XLSX cell values, never formulas, macros or external links."""
    try:
        with zipfile.ZipFile(io.BytesIO(body)) as archive:
            if sum(i.file_size for i in archive.infolist()) > 30_000_000:
                raise PublicSourceError("xlsx_expanded_size_limit")
            if len(archive.infolist()) > 100:
                raise PublicSourceError("xlsx_member_limit")
            shared = []
            if "xl/sharedStrings.xml" in archive.namelist():
                shared = ["".join(t.text or "" for t in s.findall(".//m:t", NS))
                          for s in ET.fromstring(archive.read("xl/sharedStrings.xml"))]
            for name in sorted(archive.namelist()):
                if not re.fullmatch(r"xl/worksheets/sheet[0-9]+\.xml", name):
                    continue
                rows, columns = [], None
                for row in ET.fromstring(archive.read(name)).findall(".//m:row", NS):
                    cells = {}
                    for cell in row.findall("m:c", NS):
                        if cell.find("m:f", NS) is not None:
                            continue
                        column = re.sub(r"[0-9]", "", cell.attrib.get("r", ""))
                        value = cell.find("m:v", NS)
                        text = value.text or "" if value is not None else ""
                        if cell.attrib.get("t") == "s":
                            text = shared[int(text)]
                        elif cell.attrib.get("t") == "inlineStr":
                            text = "".join(t.text or "" for t in cell.findall(".//m:t", NS))
                        cells[column] = text
                    if "CODICE_ATECO_2025" in cells.values():
                        columns = {v: k for k, v in cells.items()}
                        continue
                    if columns and "TITOLO_ITALIANO_ATECO_2025" in columns:
                        code = cells.get(columns["CODICE_ATECO_2025"], "")
                        title = cells.get(columns["TITOLO_ITALIANO_ATECO_2025"], "")
                        if code and title:
                            rows.append({"code": code, "title_it": title,
                                         "classification": "ATECO 2025"})
                if rows:
                    if len({r["code"] for r in rows}) != len(rows):
                        raise PublicSourceError("duplicate_ateco_code")
                    return rows
    except (zipfile.BadZipFile, ET.ParseError, KeyError, IndexError, ValueError):
        raise PublicSourceError("invalid_ateco_workbook") from None
    raise PublicSourceError("ateco_columns_not_found")


def eurostat_rows(data: dict) -> list[dict]:
    if data.get("class") != "dataset" or not data.get("id"):
        raise PublicSourceError("invalid_jsonstat_dataset")
    dimensions, sizes = data["id"], data.get("size", [])
    if len(dimensions) != len(sizes) or any(type(s) is not int or s < 1 for s in sizes):
        raise PublicSourceError("invalid_jsonstat_dimensions")
    if math.prod(sizes) > 1000:
        raise PublicSourceError("sample_cell_limit")
    codes, labels = [], {}
    for dimension, size in zip(dimensions, sizes, strict=True):
        category = data["dimension"][dimension]["category"]
        index = category["index"]
        if isinstance(index, dict) and set(index.values()) != set(range(size)):
            raise PublicSourceError("invalid_jsonstat_index")
        ordered = sorted(index, key=index.get) if isinstance(index, dict) else index
        if len(ordered) != size:
            raise PublicSourceError("invalid_jsonstat_index")
        codes.append(ordered)
        labels[dimension] = category.get("label", {})
    values = data.get("value", {})
    flags = data.get("status", {})

    def at(container, index):
        if isinstance(container, list):
            return container[index] if index < len(container) else None
        return container.get(str(index))

    return [{"dimensions": dict(zip(dimensions, coordinate, strict=True)),
             "dimension_labels": {d: labels[d].get(c) for d, c in
                                  zip(dimensions, coordinate, strict=True)},
             "value": at(values, i), "status_flag": at(flags, i),
             "dataset_updated": data.get("updated"), "dataset_label": data.get("label")}
            for i, coordinate in enumerate(product(*codes))]


def normalize(source: str, body: bytes) -> list[dict]:
    if source == "istat_ateco":
        return ateco_rows(body)
    try:
        data = json.loads(body)
        if source == "eurostat":
            return eurostat_rows(data)
        if source == "openalex":
            rows = [{k: row.get(k) for k in ("id", "title", "doi", "publication_year", "type")}
                    for row in data["results"]]
            if any(not row["id"] or not row["title"] for row in rows):
                raise PublicSourceError("invalid_work_identity")
            return rows
        if source == "esco":
            return [{"uri": row["uri"], "title": row["title"], "class_name": row.get("className")}
                    for row in data["_embedded"]["results"]]
    except (ValueError, TypeError, KeyError, AttributeError):
        raise PublicSourceError("invalid_source_payload") from None
    raise PublicSourceError("unknown_source")
