#pragma once
#include "layer.h"
#include <vector>
#include <string>

// A Network is a stack of layers.
// Data flows forward through all layers during forward pass.
// Gradients flow backward through all layers during backward pass.


class Network {
public:
    std::vector<Layer> layers;
    double learning_rate;

    Network(double learning_rate = 0.01);

    // Add a layer to the network
    void add_layer(int input_size, int output_size,
                   std::string activation = "relu");

    // Forward pass through all layers
    Matrix forward(const Matrix& input);

    // Backward pass through all layers in reverse
    // Takes the initial gradient from the loss function
    void backward(const Matrix& grad_loss);

    // Train on a single sample
    // Returns the loss value for monitoring
    double train_sample(const Matrix& input, const Matrix& target);

    // Mean squared error loss
    // MSE = (1/n) * sum((output - target)^2)
    // Used for both regression and autoencoder reconstruction
    static double mse_loss(const Matrix& output, const Matrix& target);

    // Gradient of MSE loss
    // dMSE/doutput = (2/n) * (output - target)
    static Matrix mse_gradient(const Matrix& output, const Matrix& target);
};