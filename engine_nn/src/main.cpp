#include <iostream>
#include <vector>
#include <cmath>
#include "nn/autoencoder.h"

int main() {
    // Simulate a dataset with 3 numeric columns:
    // age (normalized 0-1), salary (normalized 0-1), years_exp (normalized 0-1)
    //
    // Normal rows cluster around age=0.3-0.5, salary=0.4-0.7, exp=0.2-0.5
    // Anomalous rows have extreme values like age=0.99 (age=99) or salary=0.0 (negative)

    Autoencoder ae(3, 2, 0.001, 0.05);

    // Normal training data — these are all "reasonable" rows
    std::vector<Matrix> normal_rows;

    auto make_row = [](double age, double salary, double exp) {
        Matrix m(3, 1);
        m.at(0,0) = age;
        m.at(1,0) = salary;
        m.at(2,0) = exp;
        return m;
    };

    // 20 normal rows — the autoencoder learns this distribution
    normal_rows.push_back(make_row(0.34, 0.52, 0.30));
    normal_rows.push_back(make_row(0.41, 0.61, 0.40));
    normal_rows.push_back(make_row(0.28, 0.45, 0.22));
    normal_rows.push_back(make_row(0.45, 0.70, 0.48));
    normal_rows.push_back(make_row(0.33, 0.50, 0.28));
    normal_rows.push_back(make_row(0.39, 0.58, 0.35));
    normal_rows.push_back(make_row(0.47, 0.65, 0.44));
    normal_rows.push_back(make_row(0.30, 0.47, 0.25));
    normal_rows.push_back(make_row(0.43, 0.63, 0.41));
    normal_rows.push_back(make_row(0.36, 0.54, 0.32));
    normal_rows.push_back(make_row(0.38, 0.57, 0.34));
    normal_rows.push_back(make_row(0.42, 0.62, 0.39));
    normal_rows.push_back(make_row(0.29, 0.46, 0.23));
    normal_rows.push_back(make_row(0.44, 0.64, 0.43));
    normal_rows.push_back(make_row(0.31, 0.48, 0.26));
    normal_rows.push_back(make_row(0.40, 0.59, 0.37));
    normal_rows.push_back(make_row(0.35, 0.53, 0.31));
    normal_rows.push_back(make_row(0.46, 0.67, 0.46));
    normal_rows.push_back(make_row(0.32, 0.49, 0.27));
    normal_rows.push_back(make_row(0.37, 0.56, 0.33));

    // Train autoencoder on normal data only
    std::cout << "Training autoencoder on normal rows...\n\n";
    ae.fit(normal_rows, 200);

    // Now test — normal rows should have low error
    // Anomalous rows should have high error
    std::cout << "\n--- Anomaly Detection Results ---\n\n";

    auto test_row = [&](const Matrix& row, std::string label) {
        double score = ae.anomaly_score(row);
        bool flagged = ae.is_anomaly(row);
        std::cout << label << "\n";
        std::cout << "  Anomaly score: " << score
                  << (flagged ? "  *** ANOMALY DETECTED ***" : "  (normal)")
                  << "\n\n";
    };

    // Normal rows — should NOT be flagged
    test_row(make_row(0.38, 0.57, 0.34), "Normal row: age=38, salary=57k, exp=8yrs");
    test_row(make_row(0.42, 0.63, 0.41), "Normal row: age=42, salary=63k, exp=10yrs");

    // Anomalous rows — should be flagged
    test_row(make_row(0.99, 0.57, 0.34), "Anomaly: age=99 (impossible)");
    test_row(make_row(0.38, 0.00, 0.34), "Anomaly: salary=0 (negative in real data)");
    test_row(make_row(0.02, 0.90, 0.80), "Anomaly: age=2, salary=90k (child executive)");
    test_row(make_row(0.50, 0.50, 0.99), "Anomaly: 99 years experience");

    return 0;
}