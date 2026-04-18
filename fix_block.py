import fileinput

inside = False

for line in fileinput.input('app.py', inplace=True):
    if 'risk_score =' in line:
        print(line, end='')
        print("""
    if risk_score > 70:
        status = "CRITICO"
    elif risk_score > 50:
        status = "INSTABILE"
    else:
        status = "STABILE"

    if total_loss < 0:
        closing = f"Stai perdendo €{abs(int(total_loss))} oggi. Se non intervieni, perderai €{abs(int(projected_loss_3m))} nei prossimi 90 giorni."
    else:
        closing = "La struttura è stabile."
""")
        inside = True
    elif 'status =' in line or 'closing =' in line:
        continue
    else:
        print(line, end='')
