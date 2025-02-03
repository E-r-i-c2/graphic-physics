import numpy as np
import re

def parse_equation(equation, x):
    # Remove spaces and convert to lowercase
    equation = equation.replace(" ", "").lower()
    
    # Handle basic equations like y=mx+b
    if "y=" in equation:
        # Remove y= part
        expr = equation.replace("y=", "")
        
        # Handle common mathematical functions
        expr = expr.replace("^", "**")  # Convert ^ to **
        expr = re.sub(r'(\d)x', r'\1*x', expr)  # Convert 2x to 2*x
        
        # Replace mathematical functions
        expr = expr.replace("sin", "np.sin")
        expr = expr.replace("cos", "np.cos")
        expr = expr.replace("tan", "np.tan")
        expr = expr.replace("sqrt", "np.sqrt")
        expr = expr.replace("abs", "np.abs")
        expr = expr.replace("pi", "np.pi")
        
        # Replace x with array reference
        expr = expr.replace("x", "x_arr")
        
        # Create namespace for evaluation
        namespace = {"x_arr": x, "np": np}
        
        try:
            return eval(expr, namespace)
        except:
            return None
    
    # Handle vertical lines (x=c)
    if equation.startswith("x="):
        try:
            x_val = float(equation[2:])
            y = np.linspace(-1000, 1000, len(x))
            x = np.full_like(y, x_val)
            return y
        except:
            return None
    
    return None 