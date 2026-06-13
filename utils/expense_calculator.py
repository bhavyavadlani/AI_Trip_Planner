class Calculator:
    @staticmethod
    def multiply(a: float, b: float) -> float:
        """
        Multiply two numbers.

        Args:
            a (float): The first number.
            b (float): The second number.

        Returns:
            float: The product of a and b.
        """
        try:
            val_a = float(str(a).replace('$', '').replace(',', '').strip())
        except ValueError:
            val_a = 0.0
        try:
            val_b = float(str(b).replace('$', '').replace(',', '').strip())
        except ValueError:
            val_b = 0.0
        return val_a * val_b
    
    @staticmethod
    def calculate_total(*x: float) -> float:
        """
        Calculate sum of the given list of numbers

        Args:
            x (list): List of floating numbers

        Returns:
            float: The sum of numbers in the list x
        """
        return sum(x)
    
    @staticmethod
    def calculate_daily_budget(total: float, days: int) -> float:
        """
        Calculate daily budget

        Args:
            total (float): Total cost.
            days (int): Total number of days

        Returns:
            float: Expense for a single day
        """
        return total / days if days > 0 else 0
    
    