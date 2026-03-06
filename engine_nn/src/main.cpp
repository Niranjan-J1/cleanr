#include <iostream>
#include <vector>
#include "nn/fuzzy_dedup.h"

int main() {
    FuzzyDedup dedup(0.3);  // lower threshold to see all scores

    std::vector<std::string> names = {
        "Bob Smith",
        "Robert Smith",
        "B. Smith",
        "Alice Johnson",
        "Alice Johnsen",
        "Olivia Martin",
        "Olivia Martinez",
        "IBM",
        "International Business Machines",
        "New York",
        "New York City",
        "NYC"
    };

    // Print raw similarity scores for every pair
    std::cout << "--- Raw Similarity Scores ---\n\n";
    for (int i = 0; i < (int)names.size(); i++) {
        for (int j = i + 1; j < (int)names.size(); j++) {
            double sim = dedup.similarity(names[i], names[j]);
            std::cout << "\"" << names[i] << "\" vs \"" << names[j] << "\""
                      << " = " << sim << "\n";
        }
    }

    std::cout << "\n--- Flagged Duplicates (threshold=0.3) ---\n\n";
    auto pairs = dedup.find_duplicates(names);
    for (const auto& p : pairs) {
        std::cout << "DUPLICATE (score=" << p.similarity << "):\n";
        std::cout << "  \"" << p.value_a << "\"\n";
        std::cout << "  \"" << p.value_b << "\"\n\n";
    }

    return 0;
}