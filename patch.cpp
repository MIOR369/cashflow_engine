std::vector<Transaction> reduce_A_dependency(std::vector<Transaction> data) {
    for (auto& t : data) {
        if (t.client == "A" && t.amount > 0) {
            double original = t.amount;
            t.amount *= 0.7;

            // 🔥 differenza redistribuita su nuovo cliente
            Transaction new_t;
            new_t.date = t.date;
            new_t.amount = original * 0.3;
            new_t.client = "DIVERSIFIED";

            data.push_back(new_t);
        }
    }
    return data;
}
