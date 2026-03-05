#pragma once
#include "network.h"
#include <vector>

// Autoencoder for unsupervised anomaly detection.
//
// Architecture:
//   Encoder: input_size → hidden → bottleneck
//   Decoder: bottleneck → hidden → input_size
//
// Training: feed normal rows, target = same row (reconstruction)
// Inference: reconstruction error = anomaly score
//
// The bottleneck forces the network to learn a compressed
// representation of what "normal" looks like.
// Anomalous rows don't fit this representation — high error.

class Autoencoder {
public:
    int input_size;
    int bottleneck_size;
    Network net;

    // Anomaly threshold — rows above this score get flagged
    // Start at 0.1, tune based on your data
    double threshold;

    Autoencoder(int input_size, int bottleneck_size,
                double learning_rate = 0.001,
                double threshold = 0.1);

    // Train on one row (unsupervised — target = input)
    double train(const Matrix& row);

    // Get reconstruction error for a row
    // This IS the anomaly score
    double anomaly_score(const Matrix& row);

    // Returns true if row is anomalous
    bool is_anomaly(const Matrix& row);

    // Train on many rows for multiple epochs
    void fit(const std::vector<Matrix>& rows, int epochs = 100);
};