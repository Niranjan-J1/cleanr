#pragma once
#include <string>
#include <vector>
#include <utility>

// Fuzzy deduplication engine.
// Detects near-duplicate entries that aren't identical strings.

struct DuplicatePair {
    int row_a;
    int row_b;
    std::string value_a;
    std::string value_b;
    double similarity;  // 0.0 to 1.0
};

class FuzzyDedup {
public:
    double threshold;  // pairs above this are flagged as duplicates

    FuzzyDedup(double threshold = 0.75);

    // Find all near-duplicate pairs in a column of string values
    // Returns pairs sorted by similarity descending
    std::vector<DuplicatePair> find_duplicates(
        const std::vector<std::string>& values
    );

    // Combined similarity score between two strings
    double similarity(const std::string& a, const std::string& b);

private:
    // Levenshtein distance — minimum edits to transform a into b
    // Operations: insert, delete, substitute (each costs 1)
    int levenshtein(const std::string& a, const std::string& b);

    // Levenshtein similarity normalized to 0-1
    // 1.0 = identical, 0.0 = completely different
    double levenshtein_similarity(const std::string& a,
                                  const std::string& b);

    // Jaccard similarity on word tokens
    // |intersection| / |union| of word sets
    double token_similarity(const std::string& a, const std::string& b);

    // Split string into lowercase tokens
    std::vector<std::string> tokenize(const std::string& s);

    // Normalize string — lowercase, trim, remove punctuation
    std::string normalize(const std::string& s);
};