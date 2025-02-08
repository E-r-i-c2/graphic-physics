import numpy as np
import re

def parse_equation(equation, x):
    # Remove spaces and convert to lowercase
    equation = equation.replace(" ", "").lower()
    
    # Extract constraints if any
    constraints = {}
    constraint_pattern = r'{([^}]+)}'
    constraint_matches = re.findall(constraint_pattern, equation)
    
    # Remove constraints from equation
    equation = re.sub(constraint_pattern, '', equation)
    
    # Parse constraints
    for constraint in constraint_matches:
        if '<' in constraint:
            var, val = constraint.split('<')
            constraints[var.strip()] = ('less', float(val))
        elif '>' in constraint:
            var, val = constraint.split('>')
            constraints[var.strip()] = ('greater', float(val))
    
    try:
        # Handle circle equations: (x^2)+(y^2)=r^2
        circle_match = re.match(r'\(x\^2\)\+\(y\^2\)=(\d+)', equation)
        if circle_match:
            radius = float(circle_match.group(1))
            y_squared = radius - x**2
            
            # Add extra points near the x-axis for smoother connection
            x_extended = np.sort(np.concatenate([
                x,
                x[np.abs(y_squared) < 1e-10],  # Add extra points where y is close to 0
                x[np.abs(y_squared) < 1e-10] + np.finfo(float).eps  # Add slightly offset points
            ]))
            
            y_squared_extended = radius - x_extended**2
            y_pos = np.sqrt(np.where(y_squared_extended >= 0, y_squared_extended, np.nan))
            y_neg = -y_pos
            
            return [y_pos, y_neg, x_extended]  # Return y values and corresponding x values
            
        # Handle identity line cases
        if equation in ['y=x', 'x=y']:
            return x
            
        # Handle horizontal lines (y=c)
        if re.match(r'^y=-?\d+\.?\d*$', equation):
            return float(equation[2:]) * np.ones_like(x)
            
        if "y=" in equation:
            # Remove y= part and handle special case for single x
            expr = equation.replace("y=", "")
            if expr.strip() == 'x':
                return x
                
            # Handle common mathematical functions
            expr = expr.replace("^", "**")  # Convert ^ to **
            expr = re.sub(r'(\d)x', r'\1*x', expr)  # Convert 2x to 2*x
            expr = re.sub(r'x(\d)', r'x**\1', expr)  # Convert x2 to x**2
            
            # Replace mathematical functions
            expr = expr.replace("sin", "np.sin")
            expr = expr.replace("cos", "np.cos")
            expr = expr.replace("tan", "np.tan")
            expr = expr.replace("sqrt", "np.sqrt")
            expr = expr.replace("abs", "np.abs")
            expr = expr.replace("pi", "np.pi")
            expr = expr.replace("e", "np.e")
            
            # Replace x with array reference
            expr = expr.replace("x", "x_arr")
            
            # Create namespace for evaluation
            namespace = {"x_arr": x, "np": np}
            
            y = eval(expr, namespace)
            
            # Apply constraints
            mask = np.ones_like(x, dtype=bool)
            for var, (op, val) in constraints.items():
                if var == 'x':
                    if op == 'less':
                        mask &= (x < val)
                    else:
                        mask &= (x > val)
                elif var == 'y':
                    if op == 'less':
                        mask &= (y < val)
                    else:
                        mask &= (y > val)
            
            # Apply mask by setting non-matching points to NaN
            y = np.where(mask, y, np.nan)
            return y
            
    except Exception as e:
        print(f"Error parsing equation: {e}")
        return None
    
    return None 