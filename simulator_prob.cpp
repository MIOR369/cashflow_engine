#include "delay_utils.h"
#include "simulator_prob.h"
#include "date_utils.h"
#include <algorithm>
#include <random>
#include <map>

// distribuzione rischio per cliente

ProbResult simulate_probabilistic(std::vector<Transaction> data,
                                  double initial_cash,
                                  int runs) {

    std::random_device rd;
    std::mt19937 gen(rd());

    int failures = 0;
    double worst_cash = 1e9;
    double best_cash = -1e9;

    for (int r = 0; r < runs; r++) {

        std::map<time_t, double> daily;

        for (auto& t : data) {
            time_t base = to_time(t.date);

            if (t.amount > 0) {
                int delay = sample_delay(t.client, gen);
                base += delay * 86400;
            }

            daily[base] += t.amount;
        }

        time_t start = daily.begin()->first;
        time_t end = daily.rbegin()->first;

        double cash = initial_cash;
        double min_cash = cash;

        for (time_t d = start; d <= end; d += 86400) {

            if (daily.count(d)) {
                cash += daily[d];
            }

            if (cash < min_cash) {
                min_cash = cash;
            }
        }

        if (min_cash < 0) failures++;

        if (min_cash < worst_cash) worst_cash = min_cash;
        if (min_cash > best_cash) best_cash = min_cash;
    }

    double failure_prob = (double)failures / runs * 100.0;

    return {failure_prob, worst_cash, best_cash};
}
