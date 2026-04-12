#pragma once
#include "parser.h"
#include <vector>
#include <string>

struct OptimizationResult {
    double revenue_factor;
    double cost_factor;
    double risk;
};

OptimizationResult optimize(std::vector<Transaction> data,
                            double initial_cash,
                            int runs);
