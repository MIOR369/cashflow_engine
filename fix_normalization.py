import fileinput

for line in fileinput.input('app.py', inplace=True):

    if 'total_loss_multi = float(sum(x["loss"] for x in all_losses))' in line:
        print("""    total_loss_abs = abs(total_loss)
    raw_sum = sum(x["loss"] for x in all_losses)

    if raw_sum > 0:
        for x in all_losses:
            x["loss"] = float((x["loss"] / raw_sum) * total_loss_abs)

    total_loss_multi = float(total_loss_abs)
""")
    else:
        print(line, end='')
