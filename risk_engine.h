#pragma once
#include "parser.h"
#include <vector>
#include <string>

struct ClientRisk {
    std::string client;
    double failure_impact; // % di simulazioni in cui contribuisce al fallimento
};

std::vector<ClientRisk> compute_client_risk(std::vector<Transaction> data,
                                            double initial_cash,
                                            int runs);
