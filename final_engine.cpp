#include "final_engine.h"
#include "multi_cause_engine.h"
#include <algorithm>

FinalReport run_final_engine(std::vector<Transaction> data,
                            double initial_cash,
                            int runs) {

    FinalReport report;

    // 🔹 CASHFLOW
    auto sim = simulate_probabilistic(data, initial_cash, runs);
    report.risk = sim.failure_probability;

    // 🔹 MARGINI
    auto margins = compute_margins(data);

    // 🔥 MULTI-CAUSE
    auto worst_list = get_worst_clients(margins, 3);

    if (!worst_list.empty()) {
        report.critical_client = worst_list[0].client;
        report.critical_margin = worst_list[0].margin;
    }

    // 🔥 DIAGNOSI MIGLIORATA
    if (report.risk > 10 && !worst_list.empty()) {
        report.diagnosis = "HIGH RISK: multiple loss-making clients + cash instability";
        report.action = "Eliminate or renegotiate top loss-making clients";
    }
    else if (report.risk > 10) {
        report.diagnosis = "CASH RISK";
        report.action = "Improve liquidity";
    }
    else if (!worst_list.empty()) {
        report.diagnosis = "MARGIN LOSS: multiple unprofitable clients";
        report.action = "Fix pricing or remove worst clients";
    }
    else {
        report.diagnosis = "STABLE";
        report.action = "Maintain structure";
    }

    return report;
}
