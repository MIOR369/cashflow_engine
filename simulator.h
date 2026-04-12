#pragma once
#include "parser.h"
#include <vector>

struct Result {
    std::string critical_date;
    double min_cash;
    int days_to_failure;
    bool failure;
};

Result simulate(std::vector<Transaction>& data, double initial_cash);
