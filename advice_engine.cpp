#include "advice_engine.h"

std::vector<Advice> generate_advice(const std::vector<DecisionResult>& decisions) {

    std::vector<Advice> output;

    for (auto& d : decisions) {

        double delta = d.new_risk - d.original_risk;

        std::string role;
        std::string suggestion;

        if (d.new_risk >= 95.0) {
            role = "CRITICAL";
            suggestion = "reduce dependency immediately";
        }
        else if (delta > 0.1) {
            role = "BUFFER";
            suggestion = "maintain or increase volume";
        }
        else if (delta < -0.5) {
            role = "RISKY";
            suggestion = "renegotiate or reduce exposure";
        }
        else {
            role = "NEUTRAL";
            suggestion = "monitor";
        }

        output.push_back({d.client, role, suggestion});
    }

    return output;
}
