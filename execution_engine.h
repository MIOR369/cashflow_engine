#pragma once
#include "structure_engine.h"
#include <vector>
#include <string>

struct ActionPlan {
    std::string strategy;
    std::vector<std::string> steps;
};

std::vector<ActionPlan> generate_plan(const std::vector<StructuralResult>& structural);
