#!/usr/bin/env python3
"""Test recommendation engine import"""

print("🔍 Starting import test...")

try:
    print("1. Importing module...")
    import backend.services.recommendation_engine as reco_module
    print("✅ Module imported successfully")
    
    print("2. Checking attributes...")
    attrs = [x for x in dir(reco_module) if not x.startswith('_')]
    print(f"Available attributes: {attrs}")
    
    print("3. Checking recommendation_engine...")
    if hasattr(reco_module, 'recommendation_engine'):
        engine = reco_module.recommendation_engine
        print(f"✅ recommendation_engine found: {type(engine)}")
        
        print("4. Testing method...")
        if hasattr(engine, 'get_content_recommendations'):
            recommendations = engine.get_content_recommendations(1, None, 3)
            print(f"✅ Method works, got {len(recommendations)} recommendations")
        else:
            print("❌ Method not found")
    else:
        print("❌ recommendation_engine not found")
        
    print("5. Testing direct import...")
    from backend.services.recommendation_engine import recommendation_engine
    print(f"✅ Direct import successful: {type(recommendation_engine)}")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()

print("🏁 Test completed")
