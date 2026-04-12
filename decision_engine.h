#pragma once
#include "parser.h"
#include <vector>
#include <string>

struct DecisionResult {
    std::string client;
    double original_risk;
    double new_risk;
};

std::vector<DecisionResult> compute_decisions(std::vector<Transaction> data,
                                              double initial_cash,
                                              int runs);
