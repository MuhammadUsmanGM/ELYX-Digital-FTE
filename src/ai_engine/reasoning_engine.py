"""
Advanced Reasoning Engine for Gold Tier Personal AI Employee System
Implements logical reasoning, mathematical problem solving, and decision making
"""
import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Union
from pathlib import Path
import re
import ast
import math
import operator
from functools import reduce

from ..utils.logger import log_activity


class LogicalReasoningEngine:
    """
    Advanced logical reasoning engine for Gold Tier AI capabilities
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Define logical operators
        self.operators = {
            'AND': lambda x, y: x and y,
            'OR': lambda x, y: x or y,
            'NOT': lambda x: not x,
            'IMPLIES': lambda x, y: (not x) or y,
            'IFF': lambda x, y: x == y,
            'XOR': lambda x, y: x != y
        }

        # Define mathematical operators
        self.math_operators = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': operator.truediv,
            '//': operator.floordiv,
            '%': operator.mod,
            '**': operator.pow,
            '^': operator.xor,
            '&': operator.and_,
            '|': operator.or_,
            '~': operator.inv
        }

        # Define comparison operators
        self.comparison_operators = {
            '==': operator.eq,
            '!=': operator.ne,
            '<': operator.lt,
            '<=': operator.le,
            '>': operator.gt,
            '>=': operator.ge
        }

    def evaluate_logical_expression(self, expression: str, variables: Dict[str, bool]) -> bool:
        """
        Evaluate a logical expression with given variable assignments

        Args:
            expression: Logical expression to evaluate (e.g., "A AND B OR NOT C")
            variables: Dictionary mapping variable names to boolean values

        Returns:
            Result of the logical expression
        """
        try:
            # Replace variable names with their values
            expr = expression.upper()

            # Replace variable names with their boolean values
            for var_name, var_value in variables.items():
                expr = expr.replace(var_name.upper(), str(var_value).upper())

            # Replace logical operators with Python equivalents
            expr = expr.replace('AND', 'and').replace('OR', 'or').replace('NOT', 'not')
            # IMPLIES(A, B) = (not A) or B — handled via operator dict, but string form needs care
            expr = expr.replace('IMPLIES', 'or').replace('IFF', '==').replace('XOR', '!=')

            # Safely evaluate the boolean expression using AST parsing
            result = self._safe_eval_bool(expr)

            log_activity("LOGICAL_EVALUATION", f"Evaluated '{expression}' as {result}", "obsidian_vault")
            return bool(result)
        except Exception as e:
            self.logger.error(f"Error evaluating logical expression: {e}")
            return False

    def _safe_eval_bool(self, expr: str) -> bool:
        """Safely evaluate a boolean expression using AST parsing.
        Only allows: True, False, and, or, not, ==, !=, parentheses."""
        try:
            tree = ast.parse(expr, mode='eval')
            for node in ast.walk(tree):
                if isinstance(node, (ast.Expression, ast.BoolOp, ast.UnaryOp,
                                     ast.Compare, ast.Constant, ast.Name,
                                     ast.And, ast.Or, ast.Not, ast.Eq, ast.NotEq)):
                    continue
                raise ValueError(f"Unsafe expression node: {type(node).__name__}")
            # Only allow True/False as names
            for node in ast.walk(tree):
                if isinstance(node, ast.Name) and node.id not in ('True', 'False'):
                    raise ValueError(f"Unsafe variable name: {node.id}")
            code = compile(tree, '<bool_expr>', 'eval')
            return bool(eval(code, {"__builtins__": {}}, {}))
        except (ValueError, SyntaxError) as e:
            self.logger.error(f"Unsafe boolean expression: {e}")
            return False

    def _safe_eval_math(self, expression: str):
        """Safely evaluate a mathematical expression using AST parsing.
        Allows: numbers, basic operators (+,-,*,/,**,//,%), math functions, parentheses."""
        allowed_names = {
            'abs': abs, 'round': round, 'min': min, 'max': max,
            'sum': sum, 'pow': pow, 'int': int, 'float': float,
            'math': math,
        }
        try:
            tree = ast.parse(expression, mode='eval')
            for node in ast.walk(tree):
                if isinstance(node, (ast.Expression, ast.BinOp, ast.UnaryOp,
                                     ast.Constant, ast.Num, ast.Call, ast.Name,
                                     ast.Attribute, ast.Add, ast.Sub, ast.Mult,
                                     ast.Div, ast.FloorDiv, ast.Mod, ast.Pow,
                                     ast.USub, ast.UAdd, ast.Tuple, ast.List)):
                    continue
                raise ValueError(f"Unsafe expression node: {type(node).__name__}")
            for node in ast.walk(tree):
                if isinstance(node, ast.Name) and node.id not in allowed_names:
                    raise ValueError(f"Unsafe name: {node.id}")
            code = compile(tree, '<math_expr>', 'eval')
            return eval(code, {"__builtins__": {}}, allowed_names)
        except (ValueError, SyntaxError) as e:
            self.logger.error(f"Unsafe math expression: {e}")
            return None

    def solve_constraint_satisfaction_problem(self, constraints: List[Dict[str, Any]],
                                            variables: List[str],
                                            domains: Dict[str, List[Any]]) -> Optional[Dict[str, Any]]:
        """
        Solve a constraint satisfaction problem

        Args:
            constraints: List of constraints in the form {'variables': [], 'condition': function}
            variables: List of variable names
            domains: Dictionary mapping variable names to their possible values

        Returns:
            Solution assignment or None if no solution exists
        """
        def backtrack(assignment: Dict[str, Any]) -> Optional[Dict[str, Any]]:
            # If all variables are assigned, check if all constraints are satisfied
            if len(assignment) == len(variables):
                if self._check_constraints(assignment, constraints):
                    return assignment.copy()
                return None

            # Get the next unassigned variable
            for var in variables:
                if var not in assignment:
                    break

            # Try each value in the domain for this variable
            for value in domains[var]:
                assignment[var] = value

                # Check if current assignment satisfies all applicable constraints
                if self._check_partial_assignment(assignment, constraints):
                    result = backtrack(assignment)
                    if result is not None:
                        return result

                # Backtrack
                del assignment[var]

            return None

        solution = backtrack({})
        if solution:
            log_activity("CSP_SOLVED", f"Solved constraint satisfaction problem with {len(solution)} variables", "obsidian_vault")
        return solution

    def _check_constraints(self, assignment: Dict[str, Any], constraints: List[Dict[str, Any]]) -> bool:
        """Check if all constraints are satisfied by the assignment"""
        for constraint in constraints:
            constraint_vars = constraint['variables']
            condition = constraint['condition']

            # Check if all variables in the constraint are assigned
            if all(var in assignment for var in constraint_vars):
                # Get the values for the constraint variables
                values = [assignment[var] for var in constraint_vars]

                # Evaluate the condition
                if not condition(*values):
                    return False

        return True

    def _check_partial_assignment(self, assignment: Dict[str, Any], constraints: List[Dict[str, Any]]) -> bool:
        """Check if partial assignment violates any constraints"""
        for constraint in constraints:
            constraint_vars = constraint['variables']

            # Check if all variables in this constraint are assigned
            if all(var in assignment for var in constraint_vars):
                condition = constraint['condition']
                values = [assignment[var] for var in constraint_vars]

                if not condition(*values):
                    return False

        return True

    def solve_mathematical_problem(self, problem: str) -> Optional[Union[float, int, str]]:
        """
        Solve a mathematical problem expressed in text

        Args:
            problem: Mathematical problem to solve

        Returns:
            Solution to the mathematical problem
        """
        try:
            # Extract mathematical expressions from the problem
            # This is a simplified approach - in a real system, this would be more sophisticated
            expression = self._extract_math_expression(problem)

            if expression:
                # Evaluate the expression safely using AST-based parser
                result = self._safe_eval_math(expression)
                if result is None:
                    return None

                log_activity("MATH_SOLVED", f"Solved mathematical problem: {problem} = {result}", "obsidian_vault")
                return result
            else:
                return None
        except Exception as e:
            self.logger.error(f"Error solving mathematical problem: {e}")
            return None

    def _extract_math_expression(self, problem: str) -> Optional[str]:
        """Extract mathematical expression from problem text"""
        # Remove common words and keep only mathematical parts
        # This is a simplified approach
        problem_lower = problem.lower()

        # Replace words with symbols
        replacements = {
            'plus': '+',
            'minus': '-',
            'times': '*',
            'multiplied by': '*',
            'divided by': '/',
            'over': '/',
            'equals': '=',
            'equal to': '=',
            'raised to the power of': '**',
            'to the power of': '**',
            'squared': '**2',
            'cubed': '**3',
            'square root of': 'math.sqrt(',
            'log base': 'math.log',
            'natural log': 'math.log',
            'sine of': 'math.sin',
            'cosine of': 'math.cos',
            'tangent of': 'math.tan'
        }

        expression = problem_lower
        for word, symbol in replacements.items():
            expression = expression.replace(word, symbol)

        # Extract only mathematical characters and numbers
        math_chars = re.findall(r'[\d\+\-\*/\(\)\.\^=<>\[\]{}%&|~!]', expression)
        math_expr = ''.join(math_chars)

        # Balance parentheses
        open_count = math_expr.count('(')
        close_count = math_expr.count(')')

        if open_count > close_count:
            math_expr += ')' * (open_count - close_count)
        elif close_count > open_count:
            # Remove excess closing parentheses
            balanced_expr = ''
            paren_count = 0
            for char in math_expr:
                if char == '(':
                    paren_count += 1
                    balanced_expr += char
                elif char == ')':
                    if paren_count > 0:
                        paren_count -= 1
                        balanced_expr += char
                else:
                    balanced_expr += char
            math_expr = balanced_expr

        return math_expr if math_expr else None

    def make_decision(self, options: List[Dict[str, Any]],
                     criteria_weights: Dict[str, float],
                     criteria_functions: Dict[str, callable]) -> Dict[str, Any]:
        """
        Make a decision based on multiple criteria and weighted evaluation

        Args:
            options: List of options to evaluate
            criteria_weights: Dictionary mapping criteria names to their weights (0-1)
            criteria_functions: Dictionary mapping criteria names to evaluation functions

        Returns:
            Best option based on weighted evaluation
        """
        best_option = None
        best_score = float('-inf')

        for option in options:
            total_score = 0

            for criterion, weight in criteria_weights.items():
                if criterion in criteria_functions:
                    try:
                        score = criteria_functions[criterion](option)
                        total_score += score * weight
                    except Exception as e:
                        self.logger.error(f"Error evaluating criterion {criterion}: {e}")
                        total_score += 0  # Default score if evaluation fails

            if total_score > best_score:
                best_score = total_score
                best_option = {
                    'option': option,
                    'score': total_score,
                    'detailed_scores': {
                        criterion: criteria_functions[criterion](option) if criterion in criteria_functions else 0
                        for criterion in criteria_weights.keys()
                    }
                }

        if best_option:
            log_activity("DECISION_MADE", f"Made decision with score {best_option['score']:.2f}", "obsidian_vault")

        return best_option

    def perform_root_cause_analysis(self, problem_description: str,
                                  known_factors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Perform root cause analysis to identify underlying causes of problems

        Args:
            problem_description: Description of the problem to analyze
            known_factors: Known contributing factors

        Returns:
            List of potential root causes with confidence scores
        """
        root_causes = []

        # Analyze problem description for potential causes
        problem_lower = problem_description.lower()

        # Common cause patterns
        cause_patterns = [
            (r'because.*', 'direct_cause'),
            (r'due to.*', 'direct_cause'),
            (r'caused by.*', 'direct_cause'),
            (r'as a result of.*', 'indirect_cause'),
            (r'owing to.*', 'indirect_cause'),
            (r'lack of.*', 'resource_deficiency'),
            (r'failure of.*', 'system_failure'),
            (r'insufficient.*', 'capacity_issue'),
            (r'poor.*', 'quality_issue'),
            (r'inadequate.*', 'capability_issue'),
            (r'miscommunication.*', 'communication_issue'),
            (r'poor coordination.*', 'coordination_issue')
        ]

        for pattern, cause_type in cause_patterns:
            matches = re.findall(pattern, problem_lower)
            for match in matches:
                root_causes.append({
                    'cause': match.strip(),
                    'type': cause_type,
                    'confidence': 0.7,  # Base confidence
                    'evidence': [problem_description]
                })

        # Analyze known factors
        for factor in known_factors:
            if 'relationship' in factor and 'cause' in factor['relationship'].lower():
                root_causes.append({
                    'cause': factor['factor'],
                    'type': 'contributing_cause',
                    'confidence': factor.get('confidence', 0.5),
                    'evidence': factor.get('evidence', [])
                })

        # Deduplicate and sort by confidence
        unique_causes = {}
        for cause in root_causes:
            cause_text = cause['cause']
            if cause_text not in unique_causes or unique_causes[cause_text]['confidence'] < cause['confidence']:
                unique_causes[cause_text] = cause

        sorted_causes = sorted(unique_causes.values(), key=lambda x: x['confidence'], reverse=True)

        log_activity("ROOT_CAUSE_ANALYSIS", f"Identified {len(sorted_causes)} potential root causes", "obsidian_vault")
        return sorted_causes

    def generate_solution_plan(self, problem: str,
                             constraints: List[str],
                             resources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a step-by-step solution plan for a problem

        Args:
            problem: Problem to solve
            constraints: List of constraints that must be satisfied
            resources: Available resources for solving the problem

        Returns:
            Solution plan with steps and resource allocation
        """
        plan = {
            'problem': problem,
            'steps': [],
            'resource_allocation': [],
            'constraints_considered': constraints,
            'estimated_duration': 0,
            'risk_factors': [],
            'success_probability': 0.0
        }

        # Analyze the problem to identify key components
        problem_analysis = self._analyze_problem(problem)

        # Generate solution steps based on problem type
        if 'scheduling' in problem_analysis.get('categories', []):
            plan['steps'] = self._generate_scheduling_steps(problem_analysis)
        elif 'resource' in problem_analysis.get('categories', []):
            plan['steps'] = self._generate_resource_allocation_steps(problem_analysis)
        elif 'optimization' in problem_analysis.get('categories', []):
            plan['steps'] = self._generate_optimization_steps(problem_analysis)
        else:
            # General problem-solving steps
            plan['steps'] = [
                {'step': 'Analyze the problem', 'description': 'Break down the problem into components'},
                {'step': 'Identify constraints', 'description': 'List all constraints that must be satisfied'},
                {'step': 'Generate possible solutions', 'description': 'Brainstorm potential approaches'},
                {'step': 'Evaluate solutions', 'description': 'Compare solutions based on criteria'},
                {'step': 'Select optimal solution', 'description': 'Choose the best approach'},
                {'step': 'Implement solution', 'description': 'Execute the chosen approach'},
                {'step': 'Monitor and adjust', 'description': 'Track progress and make adjustments'}
            ]

        # Allocate resources to steps
        for i, step in enumerate(plan['steps']):
            if resources:
                # Assign a resource to this step
                resource_idx = i % len(resources)
                plan['resource_allocation'].append({
                    'step_index': i,
                    'step': step['step'],
                    'assigned_resource': resources[resource_idx],
                    'estimated_time': 1.0  # Default time estimate
                })

        # Calculate estimated duration
        plan['estimated_duration'] = len(plan['steps']) * 1.0  # Simplified calculation

        # Assess risks
        plan['risk_factors'] = self._identify_risks(problem_analysis, constraints)

        # Estimate success probability
        plan['success_probability'] = self._estimate_success_probability(
            len(plan['steps']),
            len(constraints),
            len(resources)
        )

        log_activity("SOLUTION_PLAN_GENERATED", f"Generated solution plan with {len(plan['steps'])} steps", "obsidian_vault")
        return plan

    def _analyze_problem(self, problem: str) -> Dict[str, Any]:
        """Analyze a problem to identify its type and components"""
        analysis = {
            'raw_problem': problem,
            'categories': [],
            'entities': [],
            'quantities': [],
            'relationships': []
        }

        problem_lower = problem.lower()

        # Identify problem categories
        categories = {
            'scheduling': ['schedule', 'timing', 'deadline', 'when', 'plan', 'arrange'],
            'resource': ['resource', 'allocate', 'assign', 'distribute', 'manage'],
            'optimization': ['optimize', 'maximize', 'minimize', 'efficient', 'best'],
            'decision': ['choose', 'select', 'decide', 'evaluate', 'compare'],
            'diagnosis': ['problem', 'issue', 'fault', 'error', 'defect'],
            'planning': ['plan', 'strategy', 'goal', 'objective', 'target']
        }

        for category, keywords in categories.items():
            if any(keyword in problem_lower for keyword in keywords):
                analysis['categories'].append(category)

        # Extract entities (capitalized words, likely proper nouns)
        entities = re.findall(r'\b[A-Z][a-zA-Z]*\b', problem)
        analysis['entities'] = list(set(entities))

        # Extract quantities (numbers with context)
        quantities = re.findall(r'(\d+(?:\.\d+)?)\s*([a-zA-Z]*)', problem_lower)
        analysis['quantities'] = [{'value': float(q[0]), 'unit': q[1] if q[1] else 'count'} for q in quantities]

        return analysis

    def _generate_scheduling_steps(self, problem_analysis: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate scheduling-specific solution steps"""
        return [
            {'step': 'List all tasks', 'description': 'Identify all tasks that need to be scheduled'},
            {'step': 'Estimate task durations', 'description': 'Determine how long each task will take'},
            {'step': 'Identify dependencies', 'description': 'Find which tasks depend on others'},
            {'step': 'Determine resource availability', 'description': 'Check when resources are available'},
            {'step': 'Create schedule', 'description': 'Develop a timeline for all tasks'},
            {'step': 'Identify critical path', 'description': 'Find the sequence of tasks that determines total duration'},
            {'step': 'Optimize schedule', 'description': 'Adjust to minimize delays and maximize efficiency'},
            {'step': 'Monitor progress', 'description': 'Track actual progress against the schedule'}
        ]

    def _generate_resource_allocation_steps(self, problem_analysis: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate resource allocation-specific solution steps"""
        return [
            {'step': 'Inventory resources', 'description': 'List all available resources'},
            {'step': 'Identify resource requirements', 'description': 'Determine what resources each task needs'},
            {'step': 'Match resources to needs', 'description': 'Assign appropriate resources to tasks'},
            {'step': 'Optimize allocation', 'description': 'Ensure efficient use of resources'},
            {'step': 'Schedule resource usage', 'description': 'Plan when resources will be used'},
            {'step': 'Monitor utilization', 'description': 'Track how effectively resources are being used'},
            {'step': 'Adjust allocation', 'description': 'Reallocate resources as needed'},
            {'step': 'Report on usage', 'description': 'Document resource consumption'}
        ]

    def _generate_optimization_steps(self, problem_analysis: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate optimization-specific solution steps"""
        return [
            {'step': 'Define objective function', 'description': 'Specify what needs to be maximized or minimized'},
            {'step': 'Identify constraints', 'description': 'List all limitations and requirements'},
            {'step': 'Formulate optimization problem', 'description': 'Express the problem mathematically'},
            {'step': 'Select optimization method', 'description': 'Choose appropriate algorithm or technique'},
            {'step': 'Solve the problem', 'description': 'Find the optimal solution'},
            {'step': 'Validate solution', 'description': 'Check that solution meets all constraints'},
            {'step': 'Implement solution', 'description': 'Put the optimal solution into practice'},
            {'step': 'Monitor performance', 'description': 'Track how well the solution performs'}
        ]

    def _identify_risks(self, problem_analysis: Dict[str, Any], constraints: List[str]) -> List[Dict[str, str]]:
        """Identify potential risks in the solution plan"""
        risks = []

        # Common risk patterns
        if 'resource' in problem_analysis.get('categories', []):
            risks.append({
                'risk': 'Resource unavailability',
                'severity': 'high',
                'mitigation': 'Maintain backup resources'
            })

        if 'scheduling' in problem_analysis.get('categories', []):
            risks.append({
                'risk': 'Timeline delays',
                'severity': 'medium',
                'mitigation': 'Include buffer time in schedule'
            })

        if 'optimization' in problem_analysis.get('categories', []):
            risks.append({
                'risk': 'Suboptimal solution',
                'severity': 'medium',
                'mitigation': 'Validate solution against alternatives'
            })

        # Analyze constraints for risks
        for constraint in constraints:
            if 'strict' in constraint.lower() or 'hard' in constraint.lower():
                risks.append({
                    'risk': f'Strict constraint violation: {constraint[:50]}...',
                    'severity': 'high',
                    'mitigation': 'Ensure strict compliance with this constraint'
                })

        return risks

    def _estimate_success_probability(self, num_steps: int, num_constraints: int, num_resources: int) -> float:
        """Estimate the probability of successfully executing the plan"""
        # Simplified estimation - in reality this would be more sophisticated
        base_probability = 0.9

        # Reduce probability based on complexity factors
        complexity_penalty = (num_steps * 0.01) + (num_constraints * 0.02)

        # Increase probability if sufficient resources are available
        resource_bonus = min(num_resources * 0.05, 0.1)  # Cap at 10%

        probability = base_probability - complexity_penalty + resource_bonus
        return max(0.1, min(0.95, probability))  # Keep between 10% and 95%


class MathematicalSolver:
    """
    Specialized mathematical problem solver
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def solve_linear_equation(self, equation: str) -> Optional[float]:
        """Solve a linear equation in the form ax + b = c"""
        try:
            # Parse the equation - this is a simplified approach
            # In a real system, this would use more sophisticated parsing
            equation = equation.replace(" ", "")

            # Look for patterns like "ax+b=c" or "ax-b=c"
            match = re.match(r'([+-]?\d*\.?\d*)x([+-]\d*\.?\d*)=([+-]?\d*\.?\d*)', equation)
            if match:
                coeff_x = match.group(1)
                const_term = match.group(2)
                result = match.group(3)

                # Handle implicit coefficient of 1
                if coeff_x == '' or coeff_x == '+':
                    coeff_x = '1'
                elif coeff_x == '-':
                    coeff_x = '-1'

                a = float(coeff_x)
                b = float(const_term)
                c = float(result)

                # Solve: ax + b = c => x = (c - b) / a
                if a != 0:
                    x = (c - b) / a
                    return x
                else:
                    return None  # No solution or infinite solutions
            else:
                return None
        except Exception as e:
            self.logger.error(f"Error solving linear equation: {e}")
            return None

    def solve_quadratic_equation(self, a: float, b: float, c: float) -> List[complex]:
        """Solve quadratic equation ax^2 + bx + c = 0"""
        discriminant = b**2 - 4*a*c

        if discriminant >= 0:
            sqrt_discriminant = math.sqrt(discriminant)
            x1 = (-b + sqrt_discriminant) / (2*a)
            x2 = (-b - sqrt_discriminant) / (2*a)
            return [x1, x2]
        else:
            # Complex solutions
            sqrt_neg_discriminant = math.sqrt(-discriminant)
            real_part = -b / (2*a)
            imag_part = sqrt_neg_discriminant / (2*a)
            x1 = complex(real_part, imag_part)
            x2 = complex(real_part, -imag_part)
            return [x1, x2]

    def find_derivative(self, expression: str, variable: str = 'x') -> str:
        """Find the derivative of a simple polynomial expression"""
        # This is a simplified implementation for basic polynomials
        # In a real system, this would use symbolic differentiation
        terms = re.split(r'(?=[+-])', expression.replace(" ", ""))

        derivative_terms = []

        for term in terms:
            if term:
                # Handle constant term
                if variable not in term:
                    continue  # Derivative of constant is 0

                # Handle term with variable
                match = re.match(r'([+-]?\d*\.?\d*)[a-zA-Z]*(\*\*[+-]?\d+)?', term)
                if match:
                    coeff = match.group(1)
                    power_match = re.search(r'\*\*(\d+)', match.group(0))

                    if power_match:
                        power = int(power_match.group(1))
                    else:
                        power = 1

                    # Handle implicit coefficient
                    if coeff == '' or coeff == '+':
                        coeff = '1'
                    elif coeff == '-':
                        coeff = '-1'

                    num_coeff = float(coeff)

                    # Apply power rule: d/dx(ax^n) = n*a*x^(n-1)
                    new_coeff = num_coeff * power
                    new_power = power - 1

                    if new_power == 0:
                        derivative_terms.append(f"{new_coeff}")
                    elif new_power == 1:
                        derivative_terms.append(f"{new_coeff}{variable}")
                    else:
                        derivative_terms.append(f"{new_coeff}{variable}**{new_power}")

        return " + ".join(derivative_terms) if derivative_terms else "0"


class DecisionSupportSystem:
    """
    Comprehensive decision support system
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.reasoning_engine = LogicalReasoningEngine()

    def perform_cost_benefit_analysis(self, options: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Perform cost-benefit analysis for different options"""
        analyzed_options = []

        for option in options:
            costs = option.get('costs', 0)
            benefits = option.get('benefits', 0)

            if isinstance(costs, (int, float)) and isinstance(benefits, (int, float)):
                net_benefit = benefits - costs
                roi = (benefits - costs) / costs if costs != 0 else float('inf')

                analyzed_options.append({
                    **option,
                    'net_benefit': net_benefit,
                    'roi': roi,
                    'cost_benefit_ratio': benefits / costs if costs != 0 else float('inf')
                })
            else:
                analyzed_options.append(option)

        # Sort by net benefit (descending)
        analyzed_options.sort(key=lambda x: x.get('net_benefit', 0), reverse=True)

        log_activity("COST_BENEFIT_ANALYSIS", f"Analyzed {len(analyzed_options)} options", "obsidian_vault")
        return analyzed_options

    def assess_risk(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risk for a given scenario"""
        probability = scenario.get('probability', 0.5)
        impact = scenario.get('impact', 1.0)

        risk_score = probability * impact

        risk_level = 'low'
        if risk_score >= 0.7:
            risk_level = 'high'
        elif risk_score >= 0.3:
            risk_level = 'medium'

        risk_assessment = {
            'scenario': scenario,
            'probability': probability,
            'impact': impact,
            'risk_score': risk_score,
            'risk_level': risk_level,
            'mitigation_suggestions': self._suggest_mitigations(risk_level, scenario)
        }

        log_activity("RISK_ASSESSED", f"Assessed risk with score {risk_score:.2f}", "obsidian_vault")
        return risk_assessment

    def _suggest_mitigations(self, risk_level: str, scenario: Dict[str, Any]) -> List[str]:
        """Suggest mitigations based on risk level and scenario"""
        suggestions = []

        if risk_level == 'high':
            suggestions.extend([
                "Implement immediate controls",
                "Escalate to senior management",
                "Develop contingency plans",
                "Monitor closely with frequent reviews"
            ])
        elif risk_level == 'medium':
            suggestions.extend([
                "Develop appropriate controls",
                "Regular monitoring and reporting",
                "Prepare response procedures",
                "Review and update risk assessment periodically"
            ])
        else:  # low
            suggestions.extend([
                "Accept the risk",
                "Continue monitoring",
                "Standard operational controls sufficient"
            ])

        return suggestions

    def generate_alternatives(self, problem: str, constraints: List[str] = None) -> List[str]:
        """Generate alternative solutions to a problem"""
        alternatives = []

        # Generate some common alternative patterns based on problem type
        problem_lower = problem.lower()

        if 'hire' in problem_lower or 'staff' in problem_lower:
            alternatives = [
                f"Outsource the {problem.split()[-1] if problem.split() else 'work'}",
                f"Automate the {problem.split()[-1] if problem.split() else 'process'}",
                f"Increase efficiency of existing staff",
                f"Redistribute workload among current employees",
                f"Contract temporary workers for the {problem.split()[-1] if problem.split() else 'work'}"
            ]
        elif 'budget' in problem_lower or 'cost' in problem_lower:
            alternatives = [
                f"Reduce non-essential expenses",
                f"Negotiate better rates with suppliers",
                f"Postpone non-critical projects",
                f"Seek additional funding sources",
                f"Optimize resource allocation"
            ]
        elif 'time' in problem_lower or 'deadline' in problem_lower:
            alternatives = [
                f"Extend the deadline",
                f"Allocate additional resources",
                f"Reduce scope of deliverables",
                f"Parallelize tasks where possible",
                f"Increase team size temporarily"
            ]
        else:
            # Generic alternatives
            alternatives = [
                f"Alternative approach 1: Change the methodology",
                f"Alternative approach 2: Modify the timeline",
                f"Alternative approach 3: Adjust resource allocation",
                f"Alternative approach 4: Revise the scope",
                f"Alternative approach 5: Seek external assistance"
            ]

        log_activity("ALTERNATIVES_GENERATED", f"Generated {len(alternatives)} alternatives", "obsidian_vault")
        return alternatives


# Example usage and testing
if __name__ == "__main__":
    print("Testing Advanced Reasoning Engine...")

    # Initialize engines
    reasoning_engine = LogicalReasoningEngine()
    math_solver = MathematicalSolver()
    decision_system = DecisionSupportSystem()

    # Test logical reasoning
    print("\n1. Testing Logical Reasoning:")
    variables = {'A': True, 'B': False, 'C': True}
    result = reasoning_engine.evaluate_logical_expression("A AND B OR NOT C", variables)
    print(f"Expression 'A AND B OR NOT C' with A=True, B=False, C=True: {result}")

    # Test constraint satisfaction
    print("\n2. Testing Constraint Satisfaction:")
    constraints = [
        {'variables': ['x', 'y'], 'condition': lambda x, y: x + y == 5},
        {'variables': ['x'], 'condition': lambda x: x > 0},
        {'variables': ['y'], 'condition': lambda y: y > 0}
    ]
    variables = ['x', 'y']
    domains = {'x': [1, 2, 3, 4], 'y': [1, 2, 3, 4]}
    solution = reasoning_engine.solve_constraint_satisfaction_problem(constraints, variables, domains)
    print(f"CSP solution: {solution}")

    # Test mathematical solving
    print("\n3. Testing Mathematical Solving:")
    result = math_solver.solve_linear_equation("2x+3=7")
    print(f"Solution to '2x+3=7': x = {result}")

    quad_solutions = math_solver.solve_quadratic_equation(1, -5, 6)  # x^2 - 5x + 6 = 0
    print(f"Solutions to x^2 - 5x + 6 = 0: {quad_solutions}")

    # Test decision making
    print("\n4. Testing Decision Making:")
    options = [
        {'name': 'Option A', 'cost': 100, 'benefit': 150, 'risk': 0.2},
        {'name': 'Option B', 'cost': 80, 'benefit': 120, 'risk': 0.3},
        {'name': 'Option C', 'cost': 120, 'benefit': 180, 'risk': 0.1}
    ]

    criteria_weights = {
        'benefit': 0.5,
        'cost_efficiency': 0.3,
        'risk': 0.2
    }

    def calc_cost_efficiency(option):
        return option['benefit'] / option['cost'] if option['cost'] != 0 else 0

    def calc_inverse_risk(option):
        return 1 - option['risk']  # Lower risk is better

    criteria_functions = {
        'benefit': lambda opt: opt['benefit'] / 200,  # Normalize
        'cost_efficiency': calc_cost_efficiency,
        'risk': calc_inverse_risk
    }

    decision = reasoning_engine.make_decision(options, criteria_weights, criteria_functions)
    print(f"Best decision: {decision['option']['name']} with score {decision['score']:.2f}")

    # Test root cause analysis
    print("\n5. Testing Root Cause Analysis:")
    problem = "The system crashed because of insufficient memory due to a memory leak in the data processing module."
    factors = [
        {'factor': 'memory leak', 'relationship': 'direct cause', 'confidence': 0.9},
        {'factor': 'high data volume', 'relationship': 'contributing factor', 'confidence': 0.7}
    ]
    causes = reasoning_engine.perform_root_cause_analysis(problem, factors)
    print(f"Root causes identified: {len(causes)}")
    for cause in causes[:2]:  # Show first 2
        print(f"  - {cause['cause']} (confidence: {cause['confidence']})")

    # Test solution planning
    print("\n6. Testing Solution Planning:")
    problem = "Schedule project tasks with limited resources"
    constraints = ["Deadline in 30 days", "Only 3 developers available", "Critical path identified"]
    resources = [
        {"name": "Dev A", "skills": ["backend"], "availability": 8},
        {"name": "Dev B", "skills": ["frontend"], "availability": 6},
        {"name": "Dev C", "skills": ["devops"], "availability": 4}
    ]
    plan = reasoning_engine.generate_solution_plan(problem, constraints, resources)
    print(f"Solution plan generated with {len(plan['steps'])} steps")
    print(f"Estimated duration: {plan['estimated_duration']} units")
    print(f"Success probability: {plan['success_probability']:.2f}")

    # Test cost-benefit analysis
    print("\n7. Testing Cost-Benefit Analysis:")
    options = [
        {'name': 'Cloud Migration', 'costs': 50000, 'benefits': 80000, 'timeline': '6 months'},
        {'name': 'On-premise Upgrade', 'costs': 30000, 'benefits': 45000, 'timeline': '3 months'},
        {'name': 'Hybrid Approach', 'costs': 40000, 'benefits': 65000, 'timeline': '4 months'}
    ]
    cb_analysis = decision_system.perform_cost_benefit_analysis(options)
    print("Cost-benefit ranked options:")
    for opt in cb_analysis[:2]:  # Show first 2
        print(f"  - {opt['name']}: Net benefit ${opt['net_benefit']:,.0f}, ROI {opt['roi']*100:.1f}%")

    print("\nAdvanced Reasoning Engine tests completed!")