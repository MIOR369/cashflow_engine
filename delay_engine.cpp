#include "delay_engine.h"
#include <cstdlib>

// modello più aggressivo

std::vector<Transaction> apply_delays(std::vector<Transaction> data) {

    for (auto& t : data) {

        if (t.amount > 0) {
            // incassi sempre ritardati forte
            t.date = "2026-06-15";
        }

        if (t.amount < 0) {
            // costi subito
            t.date = "2026-04-01";
        }
    }

    return data;
}
