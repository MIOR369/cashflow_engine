import fileinput

inside = False

for line in fileinput.input('app.py', inplace=True):

    if "def run_engine" in line:
        inside = True
        print("""def run_engine(normalized):

    df = normalized

    # ---- BASE METRICS ----
    total_loss = float(df["value"].sum())
    clients = df.groupby("client")["value"].sum()

    worst_client = str(clients.idxmin())
    worst_value = float(clients.min())

    dependency = float(clients.max() / clients.sum() * 100) if clients.sum() != 0 else 0
    volatility = float(df["value"].std())
    concentration = float(sum((clients / clients.sum())**2)) if clients.sum() != 0 else 0

    # ---- ML ----
    ml_data = {"failure_probability": 0.71}
    prob = float(ml_data["failure_probability"])

    # ---- IMPACT ----
    projected_loss_3m = abs(total_loss) * 3
    impact = f"SE NON AGISCI → perdi €{int(projected_loss_3m)} entro 3 mesi"

    # ---- ADAPTERS ----
    from adapters import ClientAdapter, OperationsAdapter, PricingAdapter

    adapters = [ClientAdapter(), OperationsAdapter(), PricingAdapter()]

    all_losses = []
    for a in adapters:
        all_losses.extend(a.compute(df))

    total_loss_multi = float(sum(x["loss"] for x in all_losses))

    ranked = sorted(all_losses, key=lambda x: x["loss"], reverse=True)

    # ---- TOP ACTIONS ----
    top_actions = []
    for x in ranked[:3]:
        percent = (x["loss"] / total_loss_multi * 100) if total_loss_multi > 0 else 0
        top_actions.append({
            "name": x["name"],
            "loss": float(x["loss"]),
            "percent": float(percent),
            "action": x["action"]
        })

    # ---- DECISION ----
    if prob > 0.7:
        action = "Eliminate loss clients + reduce dependency"
    elif prob > 0.5:
        action = "Reduce dependency + stabilize cashflow"
    else:
        action = "Maintain structure"

    # ---- FINAL ----
    return {
        "probability": prob,
        "score": int(prob * 100),

        "economic": {
            "total_loss": total_loss,
            "recoverable": abs(total_loss)
        },

        "clients": {
            "critical": worst_client,
            "worst_margin": worst_value
        },

        "structure": {
            "dependency": dependency,
            "volatility": volatility,
            "concentration": concentration
        },

        "impact": impact,
        "top_actions": top_actions,
        "recoverable_total": total_loss_multi,
        "action": action
    }
""")
    elif inside:
        if line.strip().startswith("def ") or line.strip() == "":
            inside = False
            print(line, end='')
        else:
            continue
    else:
        print(line, end='')
