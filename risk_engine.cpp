#include "delay_utils.h"
#include "risk_engine.h"
#include "date_utils.h"
#include <map>
#include <random>
#include <algorithm>


std::vector<ClientRisk> compute_client_risk(std::vector<Transaction> data,
                                            double initial_cash,
                                            int runs) {

    std::random_device rd;
    std::mt19937 gen(rd());

    std::map<std::string, int> blame_count;
    std::map<std::string, int> total_count;

    for (auto& t : data) {
        if (t.amount > 0)
            total_count[t.client]++;
    }

    for (int r = 0; r < runs; r++) {

        std::map<time_t, double> daily;
        std::map<std::string, bool> delayed;

        for (auto& t : data) {
            time_t base = to_time(t.date);

            if (t.amount > 0) {
                int delay = sample_delay(t.client, gen);
                if (delay > 0) delayed[t.client] = true;
                base += delay * 86400;
            }

            daily[base] += t.amount;
        }

        double cash = initial_cash;
        double min_cash = cash;

        time_t start = daily.begin()->first;
        time_t end = daily.rbegin()->first;

        for (time_t d = start; d <= end; d += 86400) {
            if (daily.count(d)) cash += daily[d];
            if (cash < min_cash) min_cash = cash;
        }

        if (min_cash < 0) {
            for (auto& d : delayed) {
                if (d.second) blame_count[d.first]++;
            }
        }
    }

    std::vector<ClientRisk> result;

    for (auto& t : total_count) {
        double impact = 0.0;
        if (t.second > 0)
            impact = (double)blame_count[t.first] / runs * 100.0;

        result.push_back({t.first, impact});
    }

    std::sort(result.begin(), result.end(),
              [](const ClientRisk& a, const ClientRisk& b) {
                  return a.failure_impact > b.failure_impact;
              });

    return result;
}
