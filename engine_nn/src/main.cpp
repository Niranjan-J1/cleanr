#include <iostream>
#include <cmath>
#include "nn/network.h"

int main() {
    // Build a small network: 2 inputs → 3 hidden → 1 output
    // Task: learn the function output = input1 * 0.5 + input2 * 0.3
    // This simulates learning a pattern from data

    Network net(0.01);  // learning rate = 0.01
    net.add_layer(2, 4, "relu");     // input → hidden
    net.add_layer(4, 1, "linear");   // hidden → output

    // Training data — 4 simple examples
    // Each pair: {input, expected output}
    std::vector<std::pair<Matrix, Matrix>> training_data;

    auto make_input = [](double a, double b) {
        Matrix m(2, 1);
        m.at(0,0) = a;
        m.at(1,0) = b;
        return m;
    };

    auto make_target = [](double val) {
        Matrix m(1, 1);
        m.at(0,0) = val;
        return m;
    };

    // Target function: output = a*0.5 + b*0.3
    training_data.push_back({make_input(1.0, 0.0), make_target(0.5)});
    training_data.push_back({make_input(0.0, 1.0), make_target(0.3)});
    training_data.push_back({make_input(1.0, 1.0), make_target(0.8)});
    training_data.push_back({make_input(0.5, 0.5), make_target(0.4)});

    // Train for 2000 epochs
    // An epoch = one pass through all training data
    std::cout << "Training...\n";
    for (int epoch = 0; epoch < 2000; epoch++) {
        double total_loss = 0.0;
        for (int i = 0; i < (int)training_data.size(); i++) {
            total_loss += net.train_sample(training_data[i].first, training_data[i].second);
        }
        if (epoch % 200 == 0) {
            std::cout << "Epoch " << epoch
                      << " — Loss: " << total_loss / training_data.size()
                      << "\n";
        }
    }

    // Test predictions after training
    std::cout << "\nPredictions after training:\n";
    auto test = [&](double a, double b, double expected) {
        Matrix input = make_input(a, b);
        Matrix output = net.forward(input);
        std::cout << "Input [" << a << ", " << b << "] "
                  << "→ Predicted: " << output.at(0,0)
                  << " | Expected: " << expected
                  << " | Error: " << std::abs(output.at(0,0) - expected)
                  << "\n";
    };

    test(1.0, 0.0, 0.5);
    test(0.0, 1.0, 0.3);
    test(1.0, 1.0, 0.8);
    test(0.5, 0.5, 0.4);

    return 0;
}