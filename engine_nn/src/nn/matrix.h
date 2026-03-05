#pragma once
#include <vector>
#include <string>
#include <stdexcept>
#include <cmath>
#include <random>
#include <functional>

class Matrix {
public:
    int rows;
    int cols;
    std::vector<double> data;

  

    // Empty matrix filled with zeros
    Matrix(int rows, int cols);

    // Matrix from existing data
    Matrix(int rows, int cols, std::vector<double> data);


    // Get element at row i, col j
    double& at(int i, int j);
    const double& at(int i, int j) const;



    Matrix multiply(const Matrix& other) const;

    // Element-wise addition
    Matrix add(const Matrix& other) const;

    // Element-wise subtraction
    Matrix subtract(const Matrix& other) const;

    // Element-wise multiplication (Hadamard product)
    // Used in backpropagation
    Matrix hadamard(const Matrix& other) const;

    // Transpose — flip rows and cols
    // (rows x cols) becomes (cols x rows)
    Matrix transpose() const;

    // Apply a function to every element
    // Used for activation functions
    Matrix apply(std::function<double(double)> fn) const;

    // Scalar multiplication
    Matrix scale(double scalar) const;


    // Fill with random values from normal distribution
    // Used for weight initialization
    void randomize(double mean = 0.0, double stddev = 0.1);

    // Fill all elements with a value
    void fill(double value);

    // Print matrix for debugging
    std::string to_string() const;

    // Shape check helper
    bool same_shape(const Matrix& other) const;
};