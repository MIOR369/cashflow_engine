#include "margin.h"
#include <unordered_map>

std::vector<ClientMargin> compute_margins(const std::vector<Transaction>& data) {

    std::unordered_map<std::string, ClientMargin> map;

    for (const auto& t : data) {
        if (map.find(t.client) == map.end()) {
            map[t.client] = {t.client, 0.0, 0.0, 0.0};
        }

        map[t.client].revenue += t.revenue;
        map[t.client].cost += t.cost;
    }

    std::vector<ClientMargin> result;

    for (auto& [client, m] : map) {
        m.margin = m.revenue - m.cost;
        result.push_back(m);
    }

    return result;
}
