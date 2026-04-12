#pragma once
#include "parser.h"
#include <vector>
#include <string>

struct StructuralResult {
    std::string strategy;
    double base_risk;
    double new_risk;
};

std::vector<StructuralResult> analyze_structure(std::vector<Transaction> data,
                                                double initial_cash,
                                                int runs);
