#include "network.h"
#include <stdexcept>
#include <iostream>

Network::Network(double learning_rate)
    : learning_rate(learning_rate) {}

void Network::add_layer(int input_size, int output_size,
                        std::string activation) {
    layers.emplace_back(input_size, output_size, activation);
}

Matrix Network::forward(const Matrix& input) {
    if (layers.empty()) {
        throw std::runtime_error("Network has no layers");
    }

    Matrix current = input;
    for (auto& layer : layers) {
        current = layer.forward(current);
    }
    return current;
}

void Network::backward(const Matrix& grad_loss) {

    Matrix grad = grad_loss;
    for (int i = (int)layers.size() - 1; i >= 0; i--) {
        grad = layers[i].backward(grad, learning_rate);
    }
}

double Network::train_sample(const Matrix& input, const Matrix& target) {
    //forward pass
    Matrix output = forward(input);

    // compute loss
    double loss = mse_loss(output, target);

    // compute loss gradient
    Matrix grad = mse_gradient(output, target);

    // backward pass, updates all weights
    backward(grad);

    return loss;
}

double Network::mse_loss(const Matrix& output, const Matrix& target) {
    // Mean Squared Error
    // For each element: (predicted - actual)^2
    // Average across all elements
    // Lower is better — zero means perfect prediction
    if (!output.same_shape(target)) {
        throw std::runtime_error("MSE loss shape mismatch");
    }

    double sum = 0.0;
    int n = output.rows * output.cols;
    for (int i = 0; i < n; i++) {
        double diff = output.data[i] - target.data[i];
        sum += diff * diff;
    }
    return sum / n;
}

Matrix Network::mse_gradient(const Matrix& output, const Matrix& target) {
    // Gradient of MSE with respect to output
    // dLoss/dOutput = (2/n) * (output - target)
    if (!output.same_shape(target)) {
        throw std::runtime_error("MSE gradient shape mismatch");
    }

    int n = output.rows * output.cols;
    Matrix grad = output.subtract(target);
    return grad.scale(2.0 / n);
}
