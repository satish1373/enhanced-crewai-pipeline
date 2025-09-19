def factorial(n: int) -> int:
    """
    Calculate the factorial of a non-negative integer n.
    
    Args:
        n (int): The number to calculate the factorial for, must be a non-negative integer.

    Returns:
        int: The factorial of the number n.
    
    Raises:
        ValueError: If n is a negative integer.
    """
    # Input validation
    if not isinstance(n, int):
        raise TypeError("Input must be an integer.")
    if n < 0:
        raise ValueError("Factorial is not defined for negative integers.")
    
    # Calculate factorial iteratively
    result = 1
    for i in range(2, n + 1):
        result *= i
        
    return result

# Recommended Test Cases
if __name__ == "__main__":
    # Standard Cases
    print(factorial(0))  # Expected: 1
    print(factorial(1))  # Expected: 1
    print(factorial(5))  # Expected: 120
    print(factorial(10)) # Expected: 3628800
    
    # Edge Case
    try:
        print(factorial(-1))  # Expected: ValueError
    except ValueError as e:
        print(e)  # Print error message

    # Performance Case
    print(factorial(20))  # Expected: 2432902008176640000