#include "csv_parser.h"
#include <fstream>
#include <sstream>
#include <stdexcept>
#include <cmath>
#include <algorithm>

CSVData CSVParser::parse(const std::string& filepath) {
    std::ifstream file(filepath);
    if (!file.is_open()) {
        throw std::runtime_error("Cannot open file: " + filepath);
    }

    CSVData data;
    std::string line;
    bool first_row = true;

    while (std::getline(file, line)) {
        // Remove carriage return if present (Windows line endings)
        if (!line.empty() && line.back() == '\r') {
            line.pop_back();
        }

        if (line.empty()) continue;

        // Parse CSV row respecting quoted fields
        std::vector<std::string> fields;
        std::string field;
        bool in_quotes = false;

        for (int i = 0; i < (int)line.size(); i++) {
            char c = line[i];
            if (c == '"') {
                in_quotes = !in_quotes;
            } else if (c == ',' && !in_quotes) {
                // Trim whitespace from field
                auto start = field.find_first_not_of(" \t");
                auto end   = field.find_last_not_of(" \t");
                fields.push_back(
                    start == std::string::npos ? "" :
                    field.substr(start, end - start + 1)
                );
                field.clear();
            } else {
                field += c;
            }
        }
        // Last field
        auto start = field.find_first_not_of(" \t");
        auto end   = field.find_last_not_of(" \t");
        fields.push_back(
            start == std::string::npos ? "" :
            field.substr(start, end - start + 1)
        );

        if (first_row) {
            // Strip whitespace from headers too
            for (auto& h : fields) {
                auto s = h.find_first_not_of(" \t");
                auto e = h.find_last_not_of(" \t");
                h = (s == std::string::npos) ? "" : h.substr(s, e - s + 1);
            }
            data.headers = fields;
            first_row = false;
        } else {
            data.rows.push_back(fields);
        }
    }

    return data;
}

std::vector<std::string> CSVParser::get_column_str(
    const CSVData& data, int col_index)
{
    std::vector<std::string> result;
    for (const auto& row : data.rows) {
        if (col_index < (int)row.size()) {
            result.push_back(row[col_index]);
        } else {
            result.push_back("");
        }
    }
    return result;
}

std::vector<double> CSVParser::get_column_numeric(
    const CSVData& data, int col_index)
{
    std::vector<double> result;
    for (const auto& row : data.rows) {
        if (col_index >= (int)row.size() || row[col_index].empty()) {
            result.push_back(std::numeric_limits<double>::quiet_NaN());
            continue;
        }
        try {
            result.push_back(std::stod(row[col_index]));
        } catch (...) {
            result.push_back(std::numeric_limits<double>::quiet_NaN());
        }
    }
    return result;
}

bool CSVParser::is_numeric_column(const CSVData& data, int col_index) {
    int total = 0;
    int numeric = 0;

    for (const auto& row : data.rows) {
        if (col_index >= (int)row.size()) continue;
        const std::string& val = row[col_index];
        if (val.empty()) continue;
        total++;

        // Reject values with dashes in the middle (phone numbers, dates)
        // A pure number can have a leading minus or decimal point
        // but not dashes in the middle like 555-123-4567 or 2021-03-15
        bool has_middle_dash = false;
        for (int i = 1; i < (int)val.size() - 1; i++) {
            if (val[i] == '-' || val[i] == '/') {
                has_middle_dash = true;
                break;
            }
        }
        if (has_middle_dash) continue;

        try {
            std::stod(val);
            numeric++;
        } catch (...) {}
    }

    if (total == 0) return false;
    return (double)numeric / total > 0.7;
}

std::vector<std::vector<double>> CSVParser::get_numeric_rows(
    const CSVData& data,
    const std::vector<int>& col_indices)
{
    std::vector<std::vector<double>> result;

    for (const auto& row : data.rows) {
        std::vector<double> numeric_row;
        bool valid = true;

        for (int col : col_indices) {
            if (col >= (int)row.size() || row[col].empty()) {
                valid = false;
                break;
            }
            try {
                numeric_row.push_back(std::stod(row[col]));
            } catch (...) {
                valid = false;
                break;
            }
        }

        if (valid) {
            result.push_back(numeric_row);
        }
    }

    return result;
}