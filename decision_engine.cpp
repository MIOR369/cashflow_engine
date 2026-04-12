#include "decision_engine.h"
#include "simulator_prob.h"
#include <set>

std::vector<DecisionResult> compute_decisions(std::vector<Transaction> data,
                                              double initial_cash,
                                              int runs) {

    std::set<std::string> clients;

    for (auto& t : data) {
        if (t.amount > 0)
            clients.insert(t.client);
    }

    auto base = simulate_probabilistic(data, initial_cash, runs);
    double base_risk = base.failure_probability;

    std::vector<DecisionResult> results;

    for (auto& c : clients) {

        std::vector<Transaction> filtered;

        for (auto& t : data) {
            if (t.client != c)
                filtered.push_back(t);
        }

        auto res = simulate_probabilistic(filtered, initial_cash, runs);

        results.push_back({c, base_risk, res.failure_probability});
    }

    return results;
}
