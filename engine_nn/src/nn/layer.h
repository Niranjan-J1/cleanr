#pragma once
#include "matrix.h"
#include <functional>
#include <string>

// Activation functions and their derivatives.

namespace Activation {

    // ReLU: f(x) = max(0, x)
    // Used in hidden layers — fast and avoids vanishing gradient
    inline double relu(double x) {
        return x > 0.0 ? x : 0.0;
    }
    inline double relu_derivative(double x) {
        return x > 0.0 ? 1.0 : 0.0;
    }

    // Sigmoid: f(x) = 1 / (1 + e^-x)
    inline double sigmoid(double x) {
        return 1.0 / (1.0 + std::exp(-x));
    }
    inline double sigmoid_derivative(double x) {
        double s = sigmoid(x);
        return s * (1.0 - s);
    }

    // Linear: f(x) = x
    // Derivative: 1
    inline double linear(double x) {
        return x;
    }
    inline double linear_derivative(double x) {
        (void)x;
        return 1.0;
    }
}

// A single fully-connected (dense) layer.

class Layer {
public:
    int input_size;
    int output_size;

    Matrix weights;  // shape: (output_size x input_size)
    Matrix biases;   // shape: (output_size x 1)

    // Stored during forward pass, needed for backprop
    Matrix last_input;   // shape: (input_size x 1)
    Matrix last_z;       // shape: (output_size x 1) — pre-activation
    Matrix last_output;  // shape: (output_size x 1) — post-activation

    // Activation function and its derivative
    std::function<double(double)> activation_fn;
    std::function<double(double)> activation_deriv;
    std::string activation_name;

    Layer(int input_size, int output_size, std::string activation = "relu");

    // Forward pass — takes input vector, returns output vector
    Matrix forward(const Matrix& input);

    // Backward pass — takes gradient from next layer
    // Updates weights and biases, returns gradient for previous layer
    Matrix backward(const Matrix& grad_output, double learning_rate);

    // Initialize weights using He initialization
    // He init: weights ~ N(0, sqrt(2/input_size))
    // This prevents signal from vanishing or exploding in deep networks
    void initialize_weights();
};