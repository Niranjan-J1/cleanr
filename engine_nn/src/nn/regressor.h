#pragma once
#include "network.h"
#include <vector>
#include <utility>

// Per-column regression network for missing value imputation.
//
// Given a row with one column missing, predict that column's value
// using all other columns as features.


class Regressor {
public:
    int input_size;   // number of columns minus 1
    int target_col;   // which column we're predicting
    Network net;

    // Normalization stats — we normalize inputs before training
    // to keep gradients stable
    std::vector<double> col_means;
    std::vector<double> col_stds;
    double target_mean;
    double target_std;

    Regressor(int total_cols, int target_col,
              double learning_rate = 0.001);

    // Train on complete rows
    // Each row is a full vector of all column values
    // The target column is separated out automatically
    void fit(const std::vector<std::vector<double>>& complete_rows,
             int epochs = 200);

    // Predict the missing value given all other column values
    // Pass in the full row with any placeholder for the missing column
    double predict(const std::vector<double>& row_without_target);

private:
    // Normalize a value using stored stats
    double normalize(double val, double mean, double std_dev);

    // Denormalize — convert prediction back to original scale
    double denormalize(double val, double mean, double std_dev);

    // Compute mean and std of a vector
    static double compute_mean(const std::vector<double>& vals);
    static double compute_std(const std::vector<double>& vals,
                              double mean);
};