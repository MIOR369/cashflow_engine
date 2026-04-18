import pandas as pd

def normalize_csv(file_path):
    # 🔥 prova multipla delimiter
    for sep in [",", ";", "\t", "|"]:
        try:
            df = pd.read_csv(file_path, sep=sep, header=None, engine="python")
            if df.shape[1] >= 3:
                break
        except:
            continue
    else:
        raise Exception("Formato CSV non valido (delimiter)")

    # 🔥 forza 3 colonne
    df = df.iloc[:, :3]
    df.columns = ["date", "client", "value"]

    # 🔥 pulizia estrema
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna()

    temp_path = "normalized.csv"
    df.to_csv(temp_path, index=False, header=False)

    return temp_path
