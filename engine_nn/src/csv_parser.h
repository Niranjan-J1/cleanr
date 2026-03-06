#pragma once
#include <string>
#include <vector>

// Simple CSV parser.
// Reads a CSV file into a 2D vector of strings.
// First row is treated as headers.

struct CSVData {
    std::vector<std::string> headers;
    std::vector<std::vector<std::string>> rows;

    int num_rows() const { return (int)rows.size(); }
    int num_cols() const { return (int)headers.size(); }
};

class CSVParser {
public:
    // Parse a CSV file — returns CSVData
    static CSVData parse(const std::string& filepath);

    // Get all values in a column as strings
    static std::vector<std::string> get_column_str(
        const CSVData& data, int col_index);

    // Get all values in a column as doubles
    // Non-numeric values become NaN
    static std::vector<double> get_column_numeric(
        const CSVData& data, int col_index);

    // Check if a column is mostly numeric (>70% parseable as double)
    static bool is_numeric_column(const CSVData& data, int col_index);

    // Get complete rows as numeric vectors for a set of numeric columns
    // Skips rows with any missing values in those columns
    static std::vector<std::vector<double>> get_numeric_rows(
        const CSVData& data,
        const std::vector<int>& col_indices);
};