#pragma once
#include "margin.h"
#include <vector>
#include <string>

struct Cause {
    std::string client;
    double margin;
};

std::vector<Cause> get_worst_clients(std::vector<ClientMargin> margins, int top_n);
