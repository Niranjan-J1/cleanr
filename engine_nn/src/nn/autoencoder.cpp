#include "autoencoder.h"
#include <iostream>

Autoencoder::Autoencoder(int input_size, int bottleneck_size,
                         double learning_rate, double threshold)
    : input_size(input_size),
      bottleneck_size(bottleneck_size),
      net(learning_rate),
      threshold(threshold)
{
    // Encoder — compress input down to bottleneck
    // Each layer roughly halves the size
    int hidden = (input_size + bottleneck_size) / 2;

    net.add_layer(input_size,    hidden,          "relu");
    net.add_layer(hidden,        bottleneck_size, "relu");

    // Decoder — expand bottleneck back to input size
    net.add_layer(bottleneck_size, hidden,      "relu");
    net.add_layer(hidden,          input_size,  "linear");
}

double Autoencoder::train(const Matrix& row) {
    // Target = input (we want the network to reconstruct itself)
    return net.train_sample(row, row);
}

double Autoencoder::anomaly_score(const Matrix& row) {
    Matrix reconstructed = net.forward(row);
    return Network::mse_loss(reconstructed, row);
}

bool Autoencoder::is_anomaly(const Matrix& row) {
    return anomaly_score(row) > threshold;
}

void Autoencoder::fit(const std::vector<Matrix>& rows, int epochs) {
    for (int epoch = 0; epoch < epochs; epoch++) {
        double total_loss = 0.0;
        for (const auto& row : rows) {
            total_loss += train(row);
        }
        if (epoch % 10 == 0) {
            std::cout << "Epoch " << epoch
                      << " — Reconstruction loss: "
                      << total_loss / rows.size() << "\n";
        }
    }
}
