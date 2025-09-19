def factorial(n: int) -> int:
    """
    Calculate the factorial of a non-negative integer n.

    Args:
        n (int): The number to calculate the factorial for, must be a non-negative integer.

    Returns:
        int: The factorial of the number n.

    Raises:
        ValueError: If n is a negative integer.
        TypeError: If the input is not an integer.
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


def run_tests():
    """
    Run a set of tests for the factorial function and print results.
    """
    test_cases = {
        "factorial(0)": (factorial(0), 1),
        "factorial(1)": (factorial(1), 1),
        "factorial(5)": (factorial(5), 120),
        "factorial(10)": (factorial(10), 3628800),
        "factorial(20)": (factorial(20), 2432902008176640000),
        "factorial(-1)": (None, ValueError),
    }

    for case, (result, expected) in test_cases.items():
        try:
            if expected is ValueError:
                # If we expect a ValueError, make sure it raises
                factorial(-1)
                print(f"{case}: X (Expected ValueError but got no error)")
            else:
                assert result == expected, f"{result} != {expected}"
                print(f"{case}: ✅ (Passed)")
        except Exception as e:
            if type(e) == ValueError and expected is ValueError:
                print(f"{case}: ✅ (Passed, ValueError raised as expected)")
            else:
                print(f"{case}: X (Failed with exception: {e})")


if __name__ == "__main__":
    run_tests()