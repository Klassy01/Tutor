#!/usr/bin/env python3

print("Testing recommendation engine...")

# Test 1: Basic file content
try:
    with open('/home/klassy/Downloads/Learning-Tutor/backend/services/recommendation_engine.py', 'r') as f:
        content = f.read()
    print(f"✅ File read successfully, {len(content)} characters")
except Exception as e:
    print(f"❌ Could not read file: {e}")
    exit(1)

# Test 2: Basic Python syntax check
try:
    import ast
    ast.parse(content)
    print("✅ File syntax is valid")
except SyntaxError as e:
    print(f"❌ Syntax error: {e}")
    exit(1)

# Test 3: Try compilation
try:
    compile(content, '/home/klassy/Downloads/Learning-Tutor/backend/services/recommendation_engine.py', 'exec')
    print("✅ File compiles successfully")
except Exception as e:
    print(f"❌ Compilation error: {e}")
    exit(1)

# Test 4: Try execution in isolated environment
try:
    import sys
    import os
    sys.path.insert(0, '/home/klassy/Downloads/Learning-Tutor')
    
    # Create isolated namespace
    namespace = {}
    exec(content, namespace)
    
    print("✅ File executed successfully")
    print(f"Namespace keys: {[k for k in namespace.keys() if not k.startswith('__')]}")
    
    if 'recommendation_engine' in namespace:
        print(f"✅ recommendation_engine found: {type(namespace['recommendation_engine'])}")
    else:
        print("❌ recommendation_engine not found in namespace")
        
except Exception as e:
    print(f"❌ Execution error: {e}")
    import traceback
    traceback.print_exc()

print("✅ Test completed")
