
auto decisions = compute_decisions(data, initial_cash, 1000);

std::cout << "\n=== DECISION ENGINE ===\n";
for (auto& d : decisions) {
    std::cout << "REMOVE " << d.client
              << " → FAILURE PROBABILITY: "
              << d.original_risk << "% → "
              << d.new_risk << "%";

    if (d.new_risk > d.original_risk)
        std::cout << " (ESSENTIAL)";
    else if (d.new_risk < d.original_risk)
        std::cout << " (RISKY)";

    std::cout << "\n";
}

return 0;
}
