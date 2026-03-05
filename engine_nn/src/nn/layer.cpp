#include "layer.h"
#include <cmath>
#include <stdexcept>

Layer::Layer(int input_size, int output_size, std::string activation)
    : input_size(input_size),
      output_size(output_size),
      weights(output_size, input_size),
      biases(output_size, 1),
      last_input(input_size, 1),
      last_z(output_size, 1),
      last_output(output_size, 1),
      activation_name(activation)
{
    // Set activation function and its derivative
    if (activation == "relu") {
        activation_fn    = Activation::relu;
        activation_deriv = Activation::relu_derivative;
    } else if (activation == "sigmoid") {
        activation_fn    = Activation::sigmoid;
        activation_deriv = Activation::sigmoid_derivative;
    } else if (activation == "linear") {
        activation_fn    = Activation::linear;
        activation_deriv = Activation::linear_derivative;
    } else {
        throw std::runtime_error("Unknown activation: " + activation);
    }

    initialize_weights();
}

void Layer::initialize_weights() {
    // He initialization for weights
    // Scale = sqrt(2.0 / input_size)
    // This keeps the variance of activations stable across layers.
    // Without this, signals either explode to infinity or
    // shrink to zero as they pass through many layers.
    double scale = std::sqrt(2.0 / input_size);
    weights.randomize(0.0, scale);
    biases.fill(0.0);  // biases start at zero
}

Matrix Layer::forward(const Matrix& input) {
    // Store input for backprop
    last_input = input;

    // z = W * input + b

    last_z = weights.multiply(input).add(biases);

    // a = activation(z)
    last_output = last_z.apply(activation_fn);

    return last_output;
}

Matrix Layer::backward(const Matrix& grad_output, double learning_rate) {
    // grad_output: gradient of loss w.r.t. this layer's output
    // shape: (output_size x 1)

    Matrix activation_grad = last_z.apply(activation_deriv);
    Matrix grad_z = grad_output.hadamard(activation_grad);

    // grad_W = grad_z × input^T
    Matrix grad_weights = grad_z.multiply(last_input.transpose());

    // grad_b = grad_z (biases have no input dependency)
    Matrix grad_biases = grad_z;

    // grad_input = W^T × grad_z
    // Shape: (input x output) × (output x 1) = (input x 1)
    Matrix grad_input = weights.transpose().multiply(grad_z);

    // W = W - learning_rate * grad_W
    // b = b - learning_rate * grad_b
    weights = weights.subtract(grad_weights.scale(learning_rate));
    biases  = biases.subtract(grad_biases.scale(learning_rate));

    return grad_input;
}
