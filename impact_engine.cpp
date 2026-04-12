#include "impact_engine.h"
#include "simulator_prob.h"
#include <algorithm>

ImpactResult compute_impact(std::vector<Transaction> data,
                            double initial_cash,
                            int runs) {

    auto margins = compute_margins(data);

    double recovered = 0.0;
    std::vector<std::string> bad_clients;

    for (auto& m : margins) {
        if (m.margin < 0) {
            recovered += -m.margin;
            bad_clients.push_back(m.client);
        }
    }

    // 🔥 FILTRO SICURO
    std::vector<Transaction> filtered;

    for (auto& t : data) {
        bool remove = false;

        for (auto& c : bad_clients) {
            if (t.client == c) {
                remove = true;
                break;
            }
        }

        if (!remove)
            filtered.push_back(t);
    }

    ImpactResult result;
    result.recovered_margin = recovered;

    // 🔥 FIX SEGFAULT
    if (filtered.empty()) {
        result.new_risk = 100.0;
        return result;
    }

    auto sim = simulate_probabilistic(filtered, initial_cash, runs);
    result.new_risk = sim.failure_probability;

    return result;
}
