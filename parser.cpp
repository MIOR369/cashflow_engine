#include "parser.h"
#include <fstream>
#include <sstream>

std::vector<Transaction> parse_csv(const std::string& filename) {
    std::vector<Transaction> data;
    std::ifstream file(filename);
    std::string line;

    while (std::getline(file, line)) {
        std::stringstream ss(line);

        std::string date, client, amount_str;

        std::getline(ss, date, ',');
        std::getline(ss, client, ',');
        std::getline(ss, amount_str, ',');

        Transaction t;
        t.date = date;
        t.client = client;
        t.amount = std::stod(amount_str);

        // per margine (semplificazione)
        if (t.amount > 0) t.revenue = t.amount;
        else t.cost = -t.amount;

        data.push_back(t);
    }

    return data;
}
