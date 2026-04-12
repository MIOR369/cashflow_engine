#pragma once
#include "parser.h"
#include <vector>
#include <string>

struct ScenarioResult {
    std::string name;
    double base_risk;
    double new_risk;
};

std::vector<ScenarioResult> run_scenarios(std::vector<Transaction> data,
                                          double initial_cash,
                                          int runs);
