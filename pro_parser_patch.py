import pandas as pd
import chardet
import re

def normalize_csv(file_path):

    # =========================
    # READ FILE
    # =========================
    with open(file_path, 'rb') as f:
        raw = f.read()

    encoding = chardet.detect(raw)['encoding'] or 'utf-8'

    try:
        content = raw.decode(encoding)
    except:
        content = raw.decode("utf-8", errors="ignore")

    # =========================
    # SPLIT MANUALE RIGHE
    # =========================
    lines = content.splitlines()

    data = []

    for line in lines:

        # skip righe vuote
        if not line.strip():
            continue

        # unifica separatori
        line = line.replace(";", ",")
        
        # rimuovi doppi spazi
        line = re.sub(r"\s+", " ", line)

        # SPLIT SAFE
        parts = [p.strip() for p in line.split(",")]

        if len(parts) < 3:
            continue

        date = parts[0]
        client = parts[1]
        value_raw = parts[2]

        # =========================
        # CLEAN VALUE
        # =========================
        value_raw = value_raw.replace("€", "")
        value_raw = value_raw.replace('"', "")
        value_raw = value_raw.replace(" ", "")
        value_raw = value_raw.replace(",", ".")

        # tieni solo numeri
        value_raw = re.sub(r"[^0-9\.\-]", "", value_raw)

        try:
            value = float(value_raw)
        except:
            continue

        data.append([date, client, value])

    # =========================
    # CREA DATAFRAME
    # =========================
    if not data:
        raise ValueError("File vuoto o completamente non valido")

    df = pd.DataFrame(data, columns=["date", "client", "value"])

    # =========================
    # DATE FIX
    # =========================
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    df = df.dropna(subset=["date"])
    df = df.reset_index(drop=True)

    return df
