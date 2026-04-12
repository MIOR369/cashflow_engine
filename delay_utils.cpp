#include "delay_utils.h"

int sample_delay(const std::string& client, std::mt19937& gen) {
    std::uniform_real_distribution<> prob(0.0, 1.0);
    double p = prob(gen);

    // BASE
    if (client == "A") {
        if (p < 0.7) return 0;
        else if (p < 0.9) return 5;
        else return 20;
    }

    if (client == "B") {
        if (p < 0.4) return 0;
        else if (p < 0.8) return 10;
        else return 30;
    }

    // 🔥 FIX REALE: clienti più grandi = più affidabili (FORTE)
    if (client == "A_STRONG") {
        if (p < 0.85) return 0;
        else if (p < 0.97) return 2;
        else return 7;
    }

    if (client == "B_STRONG") {
        if (p < 0.75) return 0;
        else if (p < 0.93) return 3;
        else return 10;
    }

    // 🔥 COST PRESSURE
    if (client == "LOW_PRESSURE") {
        if (p < 0.85) return 0;
        else return 3;
    }

    return 0;
}
