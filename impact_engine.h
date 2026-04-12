#pragma once
#include "margin.h"
#include "parser.h"
#include <vector>

struct ImpactResult {
    double recovered_margin;
    double new_risk;
};

ImpactResult compute_impact(std::vector<Transaction> data,
                            double initial_cash,
                            int runs);
