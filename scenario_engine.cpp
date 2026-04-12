#include "scenario_engine.h"
#include "simulator_prob.h"

// 🔹 SOLO scaling, niente manipolazione client
std::vector<Transaction> apply_revenue_boost(std::vector<Transaction> data, double factor) {
    for (auto& t : data) {
        if (t.amount > 0)
            t.amount *= factor;
    }
    return data;
}

std::vector<Transaction> apply_cost_reduction(std::vector<Transaction> data, double factor) {
    for (auto& t : data) {
        if (t.amount < 0)
            t.amount *= factor;
    }
    return data;
}

std::vector<ScenarioResult> run_scenarios(std::vector<Transaction> data,
                                          double initial_cash,
                                          int runs) {

    std::vector<ScenarioResult> results;

    auto base = simulate_probabilistic(data, initial_cash, runs);
    double base_risk = base.failure_probability;

    auto boosted = apply_revenue_boost(data, 1.2);
    auto res1 = simulate_probabilistic(boosted, initial_cash, runs);
    results.push_back({"+20% REVENUE", base_risk, res1.failure_probability});

    auto reduced = apply_cost_reduction(data, 0.9);
    auto res2 = simulate_probabilistic(reduced, initial_cash, runs);
    results.push_back({"-10% COSTS", base_risk, res2.failure_probability});

    return results;
}
