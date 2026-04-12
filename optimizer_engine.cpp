#include "optimizer_engine.h"
#include "simulator_prob.h"

// riuso funzioni semplici
std::vector<Transaction> apply_factors(std::vector<Transaction> data,
                                       double rev_factor,
                                       double cost_factor) {
    for (auto& t : data) {
        if (t.amount > 0)
            t.amount *= rev_factor;
        else if (t.amount < 0)
            t.amount *= cost_factor;
    }
    return data;
}

OptimizationResult optimize(std::vector<Transaction> data,
                            double initial_cash,
                            int runs) {

    double best_risk = 1e9;
    OptimizationResult best{1.0, 1.0, best_risk};

    // 🔥 GRID SEARCH SEMPLICE
    for (double rev = 1.0; rev <= 1.3; rev += 0.05) {
        for (double cost = 1.0; cost >= 0.7; cost -= 0.05) {

            auto modified = apply_factors(data, rev, cost);
            auto res = simulate_probabilistic(modified, initial_cash, runs);

            if (res.failure_probability < best_risk) {
                best_risk = res.failure_probability;
                best = {rev, cost, best_risk};
            }
        }
    }

    return best;
}
