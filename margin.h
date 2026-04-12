#pragma once
#include "parser.h"
#include <vector>
#include <string>

struct ClientMargin {
    std::string client;
    double revenue;
    double cost;
    double margin;
};

std::vector<ClientMargin> compute_margins(const std::vector<Transaction>& data);
