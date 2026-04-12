#include <fstream>
#include "impact_engine.h"
#include <iostream>
#include <algorithm>

#include "parser.h"
#include "margin.h"
#include "simulator.h"
#include "simulator_prob.h"
#include "risk_engine.h"
#include "optimizer_engine.h"
#include "structure_engine.h"
#include "execution_engine.h"
#include "final_engine.h"
#include "multi_cause_engine.h"
#include "delay_engine.h"

int main(int argc, char* argv[]) {

    if (argc < 3) {
        std::cout << "Usage: ./cashflow data.csv initial_cash\n";
        return 1;
    }

    std::string file = argv[1];
    double initial_cash = std::stod(argv[2]);

    auto data = parse_csv(file);

    // =========================
    // CASHFLOW
    // =========================
    std::cout << "\n=== CASHFLOW ANALYSIS ===\n\n";

    auto res = simulate(data, initial_cash);

    std::cout << (res.failure ? "FAILURE DETECTED\n" : "NO FAILURE DETECTED\n");
    std::cout << "MIN CASH: " << res.min_cash << "€\n";

    // =========================
    // PROBABILISTIC
    // =========================
    std::cout << "\n=== PROBABILISTIC ANALYSIS ===\n";

    auto delayed = apply_delays(data);
    auto prob = simulate_probabilistic(delayed, initial_cash, 500);

    std::cout << "FAILURE PROBABILITY: " << prob.failure_probability << "%\n";

    // =========================
    // CLIENT RISK
    // =========================
    std::cout << "\n=== CLIENT RISK RANKING ===\n";

    auto risks = compute_client_risk(data, initial_cash, 500);

    for (auto& r : risks) {
        std::cout << r.client << "\n";  // stampa solo client (campo certo)
    }

    // =========================
    // OPTIMIZATION
    // =========================
    std::cout << "\n=== OPTIMIZATION RESULT ===\n";

    auto opt = optimize(data, initial_cash, 500);

    std::cout << "FAILURE PROBABILITY: " << opt.risk << "%\n";

    // =========================
    // STRUCTURE
    // =========================
    std::cout << "\n=== STRUCTURAL STRATEGY ===\n";

    auto structural = analyze_structure(data, initial_cash, 500);

    for (auto& s : structural) {
        std::cout << s.strategy << "\n";
    }

    // =========================
    // EXECUTION PLAN
    // =========================
    std::cout << "\n=== OPERATIONAL PLAN ===\n";

    auto plans = generate_plan(structural);

    for (auto& p : plans) {
        std::cout << "STRATEGY: " << p.strategy << "\n";
        int i = 1;
        for (auto& step : p.steps) {
            std::cout << i++ << ". " << step << "\n";
        }
        std::cout << "\n";
    }

    // =========================
    // MARGIN
    // =========================
    std::cout << "\n=== CLIENT MARGIN RANKING ===\n\n";

    auto margins = compute_margins(data);

    std::sort(margins.begin(), margins.end(), [](auto& a, auto& b) {
        return a.margin > b.margin;
    });

    for (auto& m : margins) {
        std::cout << m.client
                  << " | Revenue: " << m.revenue
                  << " | Cost: " << m.cost
                  << " | Margin: " << m.margin;

        if (m.margin < 0)
            std::cout << "  <-- LOSS";

        std::cout << "\n";
    }

    // =========================
    // FINAL
    // =========================
    auto final = run_final_engine(data, initial_cash, 500);

    std::cout << "\n=== FINAL DIAGNOSTIC ===\n";
    std::cout << "RISK: " << final.risk << "%\n";
    std::cout << "CRITICAL CLIENT: " << final.critical_client << "\n";
    std::cout << "CLIENT MARGIN: " << final.critical_margin << "€\n\n";

    std::cout << "DIAGNOSIS: " << final.diagnosis << "\n";
    std::cout << "ACTION: " << final.action << "\n";

    // =========================
    // MULTI-CAUSE
    // =========================
    std::cout << "\nCRITICAL CLIENTS:\n";

    auto worst = get_worst_clients(margins, 3);

    for (auto& c : worst) {
        std::cout << "- " << c.client << " → " << c.margin << "€\n";
    }

    // =========================
    // IMPACT ANALYSIS
    // =========================
    std::cout << "\n=== IMPACT ANALYSIS ===\n";
    auto impact = compute_impact(data, initial_cash, 500);
    std::cout << "TOTAL RECOVERY: +" << impact.recovered_margin << "€\n";
    std::cout << "RISK AFTER ACTION: " << impact.new_risk << "%\n";

    // =========================
    // JSON OUTPUT
    // =========================
    std::ofstream json("output.json");

    json << "{\n";
    json << "\"risk\": " << final.risk << ",\n";
    json << "\"critical_client\": \"" << final.critical_client << "\",\n";
    json << "\"margin\": " << final.critical_margin << ",\n";
    json << "\"diagnosis\": \"" << final.diagnosis << "\",\n";
    json << "\"action\": \"" << final.action << "\"\n";
    json << "}\n";

    json.close();

    // =========================
    // JSON OUTPUT
    // =========================

    return 0;
}
