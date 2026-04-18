class BaseAdapter:
    def compute(self, df):
        return []

class ClientAdapter(BaseAdapter):
    def compute(self, df):
        losses = []
        clients = df.groupby("client")["value"].sum()
        for c, v in clients.items():
            if v < 0:
                losses.append({
                    "name": f"Cliente {c}",
                    "loss": float(abs(v)),
                    "action": f"Rinegozia o elimina cliente {c}"
                })
        return losses

class OperationsAdapter(BaseAdapter):
    def compute(self, df):
        losses = []
        avg = df["value"].mean()
        ineff = df[df["value"] < avg]["value"].sum()
        if ineff < 0:
            losses.append({
                "name": "Inefficienza operativa",
                "loss": float(abs(ineff)),
                "action": "Aumenta produttività o riduci costi"
            })
        return losses

class PricingAdapter(BaseAdapter):
    def compute(self, df):
        losses = []
        avg = df["value"].mean()
        if avg < 0:
            losses.append({
                "name": "Prezzi troppo bassi",
                "loss": float(abs(avg * len(df))),
                "action": "Aumenta prezzo medio"
            })
        return losses
