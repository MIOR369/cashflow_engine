#include "simulator.h"
#include "date_utils.h"
#include <algorithm>
#include <map>

Result simulate(std::vector<Transaction>& data, double initial_cash) {

    std::map<time_t, double> daily;

    for (auto& t : data) {
        daily[to_time(t.date)] += t.amount;
    }

    time_t start = daily.begin()->first;
    time_t end = daily.rbegin()->first;

    double cash = initial_cash;
    double min_cash = cash;
    std::string critical_date = "";
    bool failure = false;
    int days = 0;
    int failure_day = -1;

    for (time_t d = start; d <= end; d += 86400) {

        if (daily.count(d)) {
            cash += daily[d];
        }

        days++;

        if (cash < min_cash) {
            min_cash = cash;
        }

        if (cash < 0 && !failure) {
            failure = true;
            critical_date = to_string_date(d);
            failure_day = days;
        }
    }

    return {critical_date, min_cash, failure_day, failure};
}
