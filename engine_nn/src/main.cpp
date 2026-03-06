#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <algorithm>
#include <cmath>
#include <limits>
#include <sstream>
#include <iomanip>

#include "csv_parser.h"
#include "json_writer.h"
#include "nn/autoencoder.h"
#include "nn/regressor.h"
#include "nn/fuzzy_dedup.h"

// --- Helper: normalize to 0-1 range ---
struct NormStats { double min_val; double max_val; };

NormStats get_norm_stats(const std::vector<double>& vals) {
    double min_val = std::numeric_limits<double>::max();
    double max_val = std::numeric_limits<double>::lowest();
    for (double v : vals) {
        if (!std::isnan(v)) {
            min_val = std::min(min_val, v);
            max_val = std::max(max_val, v);
        }
    }
    return {min_val, max_val};
}

double norm(double v, NormStats s) {
    double range = s.max_val - s.min_val;
    if (range < 1e-8) return 0.5;
    return (v - s.min_val) / range;
}

// --- Helper: check if column is name-like ---
bool is_name_column(const std::string& header) {
    std::string lower = header;
    std::transform(lower.begin(), lower.end(), lower.begin(), ::tolower);
    std::vector<std::string> hints = {
        "name", "company", "entity", "employer",
        "city", "address", "organisation", "organization"
    };
    for (const auto& hint : hints) {
        if (lower.find(hint) != std::string::npos) return true;
    }
    return false;
}

// --- Task 1: Anomaly Detection ---
void run_anomaly_detection(const CSVData& data,
                           const std::string& output_path) {
    std::vector<int> numeric_cols;
    for (int i = 0; i < data.num_cols(); i++) {
        if (CSVParser::is_numeric_column(data, i))
            numeric_cols.push_back(i);
    }

    std::ofstream out(output_path);

    if (numeric_cols.empty() || data.num_rows() < 5) {
        out << "{\"task\":\"anomalies\",\"anomalies\":[]}\n";
        return;
    }

    int input_size = (int)numeric_cols.size();
    auto complete_rows = CSVParser::get_numeric_rows(data, numeric_cols);

    if ((int)complete_rows.size() < 5) {
        out << "{\"task\":\"anomalies\",\"anomalies\":[]}\n";
        return;
    }

    // Compute normalization stats per column
    std::vector<NormStats> stats;
    for (int ci = 0; ci < input_size; ci++) {
        std::vector<double> col_vals;
        for (const auto& row : complete_rows)
            col_vals.push_back(row[ci]);
        stats.push_back(get_norm_stats(col_vals));
    }

    // Build normalized training matrices
    std::vector<Matrix> training_rows;
    for (int ri = 0; ri < (int)complete_rows.size(); ri++) {
        Matrix m(input_size, 1);
        for (int ci = 0; ci < input_size; ci++)
            m.at(ci, 0) = norm(complete_rows[ri][ci], stats[ci]);
        training_rows.push_back(m);
    }

    // Train autoencoder
    int bottleneck = std::max(2, input_size / 2);
    Autoencoder ae(input_size, bottleneck, 0.001, 0.15);
    ae.fit(training_rows, 150);

    // Score every row
    std::vector<std::pair<int,double>> anomalies;
    for (int row_idx = 0; row_idx < data.num_rows(); row_idx++) {
        const auto& row = data.rows[row_idx];
        Matrix m(input_size, 1);
        bool skip = false;

        for (int ci = 0; ci < input_size; ci++) {
            int col = numeric_cols[ci];
            if (col >= (int)row.size() || row[col].empty()) {
                skip = true; break;
            }
            try {
                m.at(ci, 0) = norm(std::stod(row[col]), stats[ci]);
            } catch (...) { skip = true; break; }
        }

        if (!skip) {
            double score = ae.anomaly_score(m);
            if (ae.is_anomaly(m))
                anomalies.push_back({row_idx, score});
        }
    }

    // Write JSON
    out << "{\n";
    out << "  \"task\": \"anomalies\",\n";
    out << "  \"numeric_columns\": [";
    for (int i = 0; i < (int)numeric_cols.size(); i++) {
        out << "\"" << JsonWriter::escape(data.headers[numeric_cols[i]]) << "\"";
        if (i < (int)numeric_cols.size()-1) out << ", ";
    }
    out << "],\n";
    out << "  \"anomalies\": [\n";
    for (int i = 0; i < (int)anomalies.size(); i++) {
        out << "    {\"row\": " << anomalies[i].first
            << ", \"score\": " << JsonWriter::number(anomalies[i].second) << "}";
        if (i < (int)anomalies.size()-1) out << ",";
        out << "\n";
    }
    out << "  ]\n}\n";

    std::cout << "Found " << anomalies.size() << " anomalies.\n";
}

// --- Task 2: Fuzzy Deduplication ---
void run_fuzzy_dedup(const CSVData& data,
                     const std::string& output_path) {
    FuzzyDedup dedup(0.45);
    std::ofstream out(output_path);

    out << "{\n  \"task\": \"fuzzy_dedup\",\n";
    out << "  \"duplicate_pairs\": [\n";

    bool first = true;
    for (int col = 0; col < data.num_cols(); col++) {
        // Only run on name-like string columns
        if (CSVParser::is_numeric_column(data, col)) continue;
        if (!is_name_column(data.headers[col])) continue;

        auto values = CSVParser::get_column_str(data, col);
        auto pairs  = dedup.find_duplicates(values);

        for (const auto& p : pairs) {
            // Skip pure case differences — handled by Python rule detector
            std::string a = p.value_a;
            std::string b = p.value_b;
            std::transform(a.begin(), a.end(), a.begin(), ::tolower);
            std::transform(b.begin(), b.end(), b.begin(), ::tolower);
            if (a == b) continue;

            if (!first) out << ",\n";
            out << "    {\n";
            out << "      \"column\": \""   << JsonWriter::escape(data.headers[col]) << "\",\n";
            out << "      \"row_a\": "      << p.row_a << ",\n";
            out << "      \"row_b\": "      << p.row_b << ",\n";
            out << "      \"value_a\": \""  << JsonWriter::escape(p.value_a) << "\",\n";
            out << "      \"value_b\": \""  << JsonWriter::escape(p.value_b) << "\",\n";
            out << "      \"similarity\": " << JsonWriter::number(p.similarity) << "\n";
            out << "    }";
            first = false;
        }
    }

    out << "\n  ]\n}\n";
    std::cout << "Fuzzy dedup complete.\n";
}

// --- Task 3: Missing Value Imputation ---
void run_impute(const CSVData& data,
                const std::string& output_path) {
    std::ofstream out(output_path);

    std::vector<int> numeric_cols;
    for (int i = 0; i < data.num_cols(); i++) {
        if (CSVParser::is_numeric_column(data, i))
            numeric_cols.push_back(i);
    }

    if ((int)numeric_cols.size() < 2) {
        out << "{\"task\":\"impute\",\"imputations\":[]}\n";
        return;
    }

    out << "{\n  \"task\": \"impute\",\n";
    out << "  \"imputations\": [\n";

    bool first_imp = true;

    for (int target_idx = 0; target_idx < (int)numeric_cols.size(); target_idx++) {
        int target_col = numeric_cols[target_idx];

        // Find rows where this column is missing
        std::vector<int> missing_rows;
        for (int r = 0; r < data.num_rows(); r++) {
            const auto& row = data.rows[r];
            if (target_col >= (int)row.size() || row[target_col].empty()) {
                missing_rows.push_back(r);
            } else {
                try { std::stod(row[target_col]); }
                catch (...) { missing_rows.push_back(r); }
            }
        }

        if (missing_rows.empty()) continue;

        // Feature columns = all numeric cols except target
        std::vector<int> feature_cols;
        for (int ci = 0; ci < (int)numeric_cols.size(); ci++) {
            if (ci != target_idx) feature_cols.push_back(numeric_cols[ci]);
        }

        // Get complete rows for training
        std::vector<int> all_cols = feature_cols;
        all_cols.push_back(target_col);
        auto complete = CSVParser::get_numeric_rows(data, all_cols);

        if ((int)complete.size() < 5) continue;

        // Format for regressor
        std::vector<std::vector<double>> reg_rows;
        for (const auto& row : complete) {
            std::vector<double> reg_row;
            for (int i = 0; i < (int)feature_cols.size(); i++)
                reg_row.push_back(row[i]);
            reg_row.push_back(row.back());
            reg_rows.push_back(reg_row);
        }

        // Train regressor
        int total_cols = (int)reg_rows[0].size();
        Regressor reg(total_cols, total_cols - 1, 0.001);
        reg.fit(reg_rows, 300);

        // Predict missing values
        for (int r : missing_rows) {
            const auto& row = data.rows[r];
            std::vector<double> features;
            bool can_predict = true;

            for (int fc : feature_cols) {
                if (fc >= (int)row.size() || row[fc].empty()) {
                    can_predict = false; break;
                }
                try {
                    features.push_back(std::stod(row[fc]));
                } catch (...) { can_predict = false; break; }
            }

            if (!can_predict) continue;

            double predicted = reg.predict(features);

            if (!first_imp) out << ",\n";
            out << "    {\n";
            out << "      \"row\": " << r << ",\n";
            out << "      \"column\": \"" << JsonWriter::escape(data.headers[target_col]) << "\",\n";
            out << "      \"predicted_value\": " << JsonWriter::number(predicted) << "\n";
            out << "    }";
            first_imp = false;
        }
    }

    out << "\n  ]\n}\n";
    std::cout << "Imputation complete.\n";
}

// --- Main CLI ---
int main(int argc, char* argv[]) {
    if (argc < 4) {
        std::cerr << "Usage:\n";
        std::cerr << "  cleanr-engine --anomalies   <input.csv> <output.json>\n";
        std::cerr << "  cleanr-engine --fuzzy-dedup <input.csv> <output.json>\n";
        std::cerr << "  cleanr-engine --impute      <input.csv> <output.json>\n";
        return 1;
    }

    std::string task        = argv[1];
    std::string input_path  = argv[2];
    std::string output_path = argv[3];

    CSVData data;
    try {
        data = CSVParser::parse(input_path);
    } catch (const std::exception& e) {
        std::cerr << "Error reading CSV: " << e.what() << "\n";
        return 1;
    }

    std::cout << "Loaded: " << data.num_rows() << " rows, "
              << data.num_cols() << " columns\n";

    try {
        if (task == "--anomalies") {
            run_anomaly_detection(data, output_path);
        } else if (task == "--fuzzy-dedup") {
            run_fuzzy_dedup(data, output_path);
        } else if (task == "--impute") {
            run_impute(data, output_path);
        } else {
            std::cerr << "Unknown task: " << task << "\n";
            return 1;
        }
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << "\n";
        return 1;
    }

    std::cout << "Output written to: " << output_path << "\n";
    return 0;
}