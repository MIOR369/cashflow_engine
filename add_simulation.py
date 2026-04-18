import fileinput

for line in fileinput.input('app.py', inplace=True):

    # Inserisci calcolo ROI dentro il loop top_actions
    if 'top_actions.append({' in line:
        print(line, end='')
        print('            "monthly_gain": float(x["loss"] * 3),')
        print('            "annual_gain": float(x["loss"] * 36),')
    elif '"action": action' in line:
        # Inserisci totale annuale
        print('        "total_annual_gain": float(total_loss_multi * 36),')
        print(line, end='')
    else:
        print(line, end='')
