#include "multi_cause_engine.h"
#include <algorithm>

std::vector<Cause> get_worst_clients(std::vector<ClientMargin> margins, int top_n) {

    std::sort(margins.begin(), margins.end(), [](const ClientMargin& a, const ClientMargin& b) {
        return a.margin < b.margin;
    });

    std::vector<Cause> result;

    for (int i = 0; i < margins.size() && i < top_n; i++) {
        if (margins[i].margin < 0) {
            result.push_back({margins[i].client, margins[i].margin});
        }
    }

    return result;
}
