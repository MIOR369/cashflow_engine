#pragma once
#include "parser.h"
#include <vector>

struct ProbResult {
    double failure_probability;
    double worst_cash;
    double best_cash;
};

ProbResult simulate_probabilistic(std::vector<Transaction> data,
                                  double initial_cash,
                                  int runs);
