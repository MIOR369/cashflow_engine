#pragma once
#include "parser.h"
#include "margin.h"
#include "simulator_prob.h"
#include <string>

struct FinalReport {
    double risk;
    std::string critical_client;
    double critical_margin;
    std::string diagnosis;
    std::string action;
};

FinalReport run_final_engine(std::vector<Transaction> data,
                            double initial_cash,
                            int runs);
