# INCOLLA QUESTO BLOCCO DENTRO app.py PRIMA DEL final = {}

# ---- SCORE ----
risk_score = int(prob * 100)

# ---- STATO AZIENDA ----
if risk_score > 70:
    status = "CRITICO"
elif risk_score > 50:
    status = "INSTABILE"
else:
    status = "STABILE"

# ---- FRASE DI CHIUSURA ----
closing = ""

if total_loss < 0:
    closing = f"Stai perdendo €{abs(int(total_loss))} oggi. Se non intervieni, la perdita stimata è €{abs(int(projected_loss_3m))} nei prossimi 90 giorni."
else:
    closing = "La struttura è stabile ma monitorare è essenziale."

# AGGIUNGI NEL FINAL:
# "score": risk_score,
# "status": status,
# "closing": closing
