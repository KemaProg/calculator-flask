from flask import Flask, render_template, request, jsonify
import math
import re

app = Flask(__name__)

class Calculator:
    def __init__(self):
        self.allowed_chars = set('0123456789+-*/().^ ')
        self.functions = {
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'sqrt': math.sqrt,
            'log': math.log10,
            'ln': math.log,
            'abs': abs,
            'pi': math.pi,
            'e': math.e
        }
    
    def evaluate(self, expression):
        try:
            # Проверяем безопасность выражения
            if not all(c in self.allowed_chars or c.isalpha() for c in expression):
                raise ValueError("Недопустимые символы в выражении")
            
            # Заменяем ^ на **
            expression = expression.replace('^', '**')
            
            # Заменяем математические функции
            for func_name, func in self.functions.items():
                if func_name in ['pi', 'e']:
                    expression = expression.replace(func_name, str(func))
                else:
                    expression = re.sub(f'\\b{func_name}\\b', f'math.{func_name}', expression)
            
            # Добавляем math. для других функций
            expression = re.sub(r'\bsqrt\b', 'math.sqrt', expression)
            expression = re.sub(r'\blog\b', 'math.log10', expression)
            expression = re.sub(r'\bln\b', 'math.log', expression)
            
            # Вычисляем результат
            result = eval(expression, {"__builtins__": {}, "math": math})
            
            # Проверяем на NaN и бесконечность
            if math.isnan(result):
                return "Ошибка: Результат не определен"
            elif math.isinf(result):
                return "Ошибка: Бесконечность"
            
            return result
        
        except ZeroDivisionError:
            return "Ошибка: Деление на ноль"
        except ValueError as e:
            return f"Ошибка: {str(e)}"
        except Exception as e:
            return f"Ошибка: Неверное выражение"

calculator = Calculator()

@app.route('/')
def index():
    return render_template('calculator.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    expression = data.get('expression', '')
    
    if not expression:
        return jsonify({'error': 'Пустое выражение'})
    
    result = calculator.evaluate(expression)
    
    return jsonify({
        'result': result,
        'expression': expression
    })

@app.route('/clear', methods=['POST'])
def clear():
    return jsonify({'message': 'Очищено'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)