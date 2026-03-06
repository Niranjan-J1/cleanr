#include "regressor.h"
#include <cmath>
#include <stdexcept>
#include <iostream>
#include <numeric>

Regressor::Regressor(int total_cols, int target_col,
                     double learning_rate)
    : input_size(total_cols - 1),
      target_col(target_col),
      net(learning_rate),
      col_means(total_cols, 0.0),
      col_stds(total_cols, 1.0),
      target_mean(0.0),
      target_std(1.0)
{
    // Simple network: input → hidden → hidden → output
    // Output is a single value (the predicted column)
    int hidden = std::max(4, input_size * 2);

    net.add_layer(input_size, hidden,   "relu");
    net.add_layer(hidden,     hidden,   "relu");
    net.add_layer(hidden,     1,        "linear");
}

void Regressor::fit(const std::vector<std::vector<double>>& complete_rows,
                    int epochs) {
    if (complete_rows.empty()) return;

    int total_cols = (int)complete_rows[0].size();

    // Compute normalization stats for each column
    // We normalize so all values are roughly in same range
    for (int col = 0; col < total_cols; col++) {
        std::vector<double> vals;
        for (const auto& row : complete_rows) {
            vals.push_back(row[col]);
        }
        col_means[col] = compute_mean(vals);
        col_stds[col]  = compute_std(vals, col_means[col]);
        if (col_stds[col] < 1e-8) col_stds[col] = 1.0; // avoid division by zero
    }

    target_mean = col_means[target_col];
    target_std  = col_stds[target_col];

    // Build normalized training pairs
    for (int epoch = 0; epoch < epochs; epoch++) {
        double total_loss = 0.0;

        for (const auto& row : complete_rows) {
            // Build input — all columns except target
            Matrix input(input_size, 1);
            int idx = 0;
            for (int col = 0; col < total_cols; col++) {
                if (col == target_col) continue;
                input.at(idx, 0) = normalize(row[col],
                                             col_means[col],
                                             col_stds[col]);
                idx++;
            }

            // Build target — normalized target column value
            Matrix target_mat(1, 1);
            target_mat.at(0, 0) = normalize(row[target_col],
                                            target_mean,
                                            target_std);

            total_loss += net.train_sample(input, target_mat);
        }

        if (epoch % 50 == 0) {
            std::cout << "  Regressor epoch " << epoch
                      << " loss: " << total_loss / complete_rows.size()
                      << "\n";
        }
    }
}

double Regressor::predict(const std::vector<double>& row_without_target) {
    if ((int)row_without_target.size() != input_size) {
        throw std::runtime_error("Regressor predict: input size mismatch");
    }

    // Normalize input
    Matrix input(input_size, 1);
    for (int i = 0; i < input_size; i++) {
        // For prediction we use the column stats but skip target_col
        // The caller passes a row with target already removed
        int col_idx = (i >= target_col) ? i + 1 : i;
        input.at(i, 0) = normalize(row_without_target[i],
                                   col_means[col_idx],
                                   col_stds[col_idx]);
    }

    // Forward pass
    Matrix output = net.forward(input);

    // Denormalize back to original scale
    return denormalize(output.at(0, 0), target_mean, target_std);
}

double Regressor::normalize(double val, double mean, double std_dev) {
    return (val - mean) / std_dev;
}

double Regressor::denormalize(double val, double mean, double std_dev) {
    return val * std_dev + mean;
}

double Regressor::compute_mean(const std::vector<double>& vals) {
    double sum = std::accumulate(vals.begin(), vals.end(), 0.0);
    return sum / vals.size();
}

double Regressor::compute_std(const std::vector<double>& vals, double mean) {
    double sum = 0.0;
    for (double v : vals) {
        sum += (v - mean) * (v - mean);
    }
    return std::sqrt(sum / vals.size());
}
