#include "fuzzy_dedup.h"
#include <algorithm>
#include <sstream>
#include <set>
#include <cctype>
#include <cmath>

FuzzyDedup::FuzzyDedup(double threshold)
    : threshold(threshold) {}

std::vector<DuplicatePair> FuzzyDedup::find_duplicates(
    const std::vector<std::string>& values)
{
    std::vector<DuplicatePair> pairs;

    // Compare every pair of values
    // O(n^2) — fine for CSV columns which are rarely > 10k rows
    for (int i = 0; i < (int)values.size(); i++) {
        for (int j = i + 1; j < (int)values.size(); j++) {
            // Skip exact duplicates — already handled by rule-based detector
            if (values[i] == values[j]) continue;

            double sim = similarity(values[i], values[j]);

            if (sim >= threshold) {
                pairs.push_back({i, j, values[i], values[j], sim});
            }
        }
    }

    // Sort by similarity descending — most likely duplicates first
    std::sort(pairs.begin(), pairs.end(),
        [](const DuplicatePair& a, const DuplicatePair& b) {
            return a.similarity > b.similarity;
        });

    return pairs;
}

double FuzzyDedup::similarity(const std::string& a, const std::string& b) {
    // Combine character-level and token-level similarity
    // Weight: 40% levenshtein + 60% token overlap
    // Token overlap weighted higher because "Bob" vs "Robert"
    // has low levenshtein but high semantic overlap
    double lev_sim   = levenshtein_similarity(a, b);
    double tok_sim   = token_similarity(a, b);
    return 0.4 * lev_sim + 0.6 * tok_sim;
}

int FuzzyDedup::levenshtein(const std::string& a, const std::string& b) {

    std::string na = normalize(a);
    std::string nb = normalize(b);

    int m = (int)na.size();
    int n = (int)nb.size();

    std::vector<std::vector<int>> dp(m + 1, std::vector<int>(n + 1, 0));

    for (int i = 0; i <= m; i++) dp[i][0] = i;
    for (int j = 0; j <= n; j++) dp[0][j] = j;

    for (int i = 1; i <= m; i++) {
        for (int j = 1; j <= n; j++) {
            if (na[i-1] == nb[j-1]) {
                dp[i][j] = dp[i-1][j-1];
            } else {
                dp[i][j] = 1 + std::min({
                    dp[i-1][j],
                    dp[i][j-1],
                    dp[i-1][j-1]
                });
            }
        }
    }

    return dp[m][n];
}

double FuzzyDedup::levenshtein_similarity(const std::string& a,
                                          const std::string& b) {
    int dist = levenshtein(a, b);
    int max_len = std::max(a.size(), b.size());
    if (max_len == 0) return 1.0;
    return 1.0 - (double)dist / max_len;
}

double FuzzyDedup::token_similarity(const std::string& a,
                                    const std::string& b) {
    // Jaccard similarity on word sets
    // Good for catching "International Business Machines" vs "IBM"
    // when combined with abbreviation expansion
    auto tokens_a = tokenize(a);
    auto tokens_b = tokenize(b);

    std::set<std::string> set_a(tokens_a.begin(), tokens_a.end());
    std::set<std::string> set_b(tokens_b.begin(), tokens_b.end());

    // Count intersection
    int intersection = 0;
    for (const auto& t : set_a) {
        if (set_b.count(t)) intersection++;
    }

    // Union size = |A| + |B| - |intersection|
    int union_size = (int)(set_a.size() + set_b.size()) - intersection;

    if (union_size == 0) return 1.0;
    return (double)intersection / union_size;
}

std::vector<std::string> FuzzyDedup::tokenize(const std::string& s) {
    std::string norm = normalize(s);
    std::istringstream ss(norm);
    std::vector<std::string> tokens;
    std::string token;
    while (ss >> token) {
        tokens.push_back(token);
    }
    return tokens;
}

std::string FuzzyDedup::normalize(const std::string& s) {
    std::string result;
    for (char c : s) {
        if (std::isalnum(c) || c == ' ') {
            result += std::tolower(c);
        } else {
            result += ' ';  // replace punctuation with space
        }
    }
    // Trim extra spaces
    std::string trimmed;
    bool last_space = false;
    for (char c : result) {
        if (c == ' ') {
            if (!last_space && !trimmed.empty()) trimmed += c;
            last_space = true;
        } else {
            trimmed += c;
            last_space = false;
        }
    }
    return trimmed;
}
