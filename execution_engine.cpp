#include "execution_engine.h"

std::vector<ActionPlan> generate_plan(const std::vector<StructuralResult>& structural) {

    std::vector<ActionPlan> plans;

    for (auto& s : structural) {

        ActionPlan plan;
        plan.strategy = s.strategy;

        if (s.strategy == "ADD STABLE CLIENT") {

            plan.steps = {
                "Identify 3 target clients similar to A",
                "Contact them within 7 days",
                "Offer initial discount (5-10%)",
                "Close at least 1 deal within 30 days",
                "Reduce dependency on A below 60%"
            };
        }

        else if (s.strategy == "REDUCE A DEPENDENCY") {

            plan.steps = {
                "Split A revenue across 2-3 clients",
                "Limit A to max 50-60% of total revenue",
                "Introduce backup clients",
                "Monitor monthly dependency ratio"
            };
        }

        else if (s.strategy == "DELAY PAYMENTS") {

            plan.steps = {
                "Negotiate supplier payment terms (+10-15 days)",
                "Align outgoing payments with incoming cash",
                "Prioritize critical suppliers",
                "Avoid early payments"
            };
        }

        plans.push_back(plan);
    }

    return plans;
}
