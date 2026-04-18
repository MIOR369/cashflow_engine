// ---- FAILURE PROBABILITY (continuous, bounded 0-1) ----

// helpers
auto clamp01 = [](double x){ return x < 0 ? 0 : (x > 1 ? 1 : x); };
auto sigmoid = [](double x){ return 1.0 / (1.0 + exp(-x)); };

// 1) loss severity (0..1)
double loss_ratio = (total_revenue > 0) ? (-worst_margin / total_revenue) : 0;
double loss_score = clamp01(loss_ratio); // più perdi vs ricavi → più alto

// 2) dependency (0..1) — già %
double dep_score = clamp01(dependency / 100.0);

// 3) volatility (0..1) — scala con sigmoid
double vol_norm = sigmoid((volatility - 400.0) / 200.0); // centro ~400, slope 200

// 4) concentration HHI (0..1)
double conc_score = clamp01(concentration); // già 0..1

// pesi (tuning)
double w_loss = 0.35;
double w_dep  = 0.25;
double w_vol  = 0.20;
double w_conc = 0.20;

// aggregazione
double failure_prob =
    w_loss * loss_score +
    w_dep  * dep_score +
    w_vol  * vol_norm +
    w_conc * conc_score;

failure_prob = clamp01(failure_prob);
