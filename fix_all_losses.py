import fileinput

inserted = False

for line in fileinput.input('app.py', inplace=True):

    if "for x in all_losses" in line and not inserted:
        print("    adapters = [ClientAdapter(), OperationsAdapter(), PricingAdapter()]")
        print("    all_losses = []")
        print("    for a in adapters:")
        print("        all_losses.extend(a.compute(df))")
        inserted = True

    print(line, end='')
