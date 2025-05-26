#!/bin/bash

# Create 'results' directory
mkdir results

# Change into the 'results' directory
cd results || exit

# Create sub-directories
mkdir behavioral designs performance summary

# Navigate back to the parent directory
cd ..

# Create 'run_results' directory
mkdir run_results

# Change into the 'run_results' directory
cd run_results || exit

# Create 'designs' sub-directory
mkdir designs

# Navigate back to the parent directory
cd ..

# Display success message
echo "Directory structure created successfully."

