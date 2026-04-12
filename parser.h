#pragma once
#include <vector>
#include <string>

struct Transaction {
    std::string date;
    std::string client;

    double amount;   // per cashflow (+ entrata, - uscita)

    // opzionali per margine
    double revenue = 0.0;
    double cost = 0.0;
};

std::vector<Transaction> parse_csv(const std::string& filename);
