#pragma once
#include "decision_engine.h"
#include <vector>
#include <string>

struct Advice {
    std::string client;
    std::string role;
    std::string suggestion;
};

std::vector<Advice> generate_advice(const std::vector<DecisionResult>& decisions);
