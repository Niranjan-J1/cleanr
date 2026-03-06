#include <iostream>
#include <vector>
#include <cmath>
#include "nn/autoencoder.h"
#include "nn/regressor.h"

int main() {
    // Simulate a dataset:
    // columns: [age, salary, years_experience]
    // We'll train a regressor to predict salary (col 1)
    // from age and years_experience

    // Complete rows for training
    // Real pattern: salary ≈ 40000 + age*500 + exp*2000
    std::vector<std::vector<double>> rows = {
        {25, 52000, 2},
        {30, 61000, 5},
        {35, 72000, 8},
        {40, 83000, 12},
        {45, 91000, 15},
        {28, 57000, 3},
        {33, 68000, 7},
        {38, 78000, 10},
        {42, 86000, 13},
        {50, 98000, 20},
        {27, 55000, 3},
        {32, 65000, 6},
        {37, 76000, 9},
        {43, 88000, 14},
        {48, 95000, 18},
    };

    // Train regressor to predict salary (column index 1)
    std::cout << "Training salary regressor...\n";
    Regressor reg(3, 1, 0.001);
    reg.fit(rows, 500);

    // Test predictions
    std::cout << "\n--- Salary Predictions ---\n\n";

    auto test = [&](double age, double exp, double actual_salary) {
        std::vector<double> input = {age, exp};
        double predicted = reg.predict(input);
        std::cout << "Age=" << age << " Exp=" << exp << "yrs"
                  << " | Predicted salary: $" << (int)predicted
                  << " | Actual: $" << (int)actual_salary
                  << " | Error: $" << (int)std::abs(predicted - actual_salary)
                  << "\n";
    };

    test(25,  2,  52000);
    test(35,  8,  72000);
    test(45, 15,  91000);
    test(31,  5,  63000);  // not in training data
    test(52, 22, 103000);  // extrapolation

    return 0;
}