// ---- RISK SCORE ----
double risk = failure_prob * 100;

// ---- DIAGNOSIS + ACTION ----
string diagnosis = "STABLE";
string action = "OK";

if (risk >= 70) {
    diagnosis = "CRITICAL: systemic risk";
    action = "Immediate restructuring";
}
else if (risk >= 40) {
    diagnosis = "HIGH RISK: instability + losses";
    action = "Reduce losses + diversify clients";
}
