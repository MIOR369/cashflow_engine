#include "structure_engine.h"
#include "simulator_prob.h"

// 🔹 aggiunge cliente nuovo stabile
std::vector<Transaction> add_stable_client(std::vector<Transaction> data) {
    Transaction t;
    t.date = "2026-04-05";
    t.amount = 2000;
    t.client = "NEW_STABLE";
    data.push_back(t);
    return data;
}

// 🔥 FIX REALE: riduzione dipendenza = redistribuzione
std::vector<Transaction> reduce_A_dependency(std::vector<Transaction> data) {
    std::vector<Transaction> new_entries;

    for (auto& t : data) {
        if (t.client == "A" && t.amount > 0) {
            double original = t.amount;

            // mantieni 70% su A
            t.amount *= 0.7;

            // crea nuovo cliente per il 30%
            Transaction new_t;
            new_t.date = t.date;
            new_t.amount = original * 0.3;
            new_t.client = "DIVERSIFIED";

            new_entries.push_back(new_t);
        }
    }

    // append fuori dal loop (no invalidation)
    data.insert(data.end(), new_entries.begin(), new_entries.end());

    return data;
}

// 🔹 ritarda pagamenti
std::vector<Transaction> delay_outflows(std::vector<Transaction> data) {
    for (auto& t : data) {
        if (t.amount < 0)
            t.date = "2026-04-20";
    }
    return data;
}

std::vector<StructuralResult> analyze_structure(std::vector<Transaction> data,
                                                double initial_cash,
                                                int runs) {

    std::vector<StructuralResult> results;

    auto base = simulate_probabilistic(data, initial_cash, runs);
    double base_risk = base.failure_probability;

    auto s1 = simulate_probabilistic(add_stable_client(data), initial_cash, runs);
    results.push_back({"ADD STABLE CLIENT", base_risk, s1.failure_probability});

    auto s2 = simulate_probabilistic(reduce_A_dependency(data), initial_cash, runs);
    results.push_back({"REDUCE A DEPENDENCY", base_risk, s2.failure_probability});

    auto s3 = simulate_probabilistic(delay_outflows(data), initial_cash, runs);
    results.push_back({"DELAY PAYMENTS", base_risk, s3.failure_probability});

    return results;
}
