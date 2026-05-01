"""Test script for backend enhancements"""
from app.services.prediction_service import adjust_portion, get_healthier_alternatives


def test_portion_adjustment():
    """Test portion size adjustment"""
    print("\n✓ Testing Portion Adjustment...")
    
    # Test half portion
    result = adjust_portion(320.0, 0.5, "half portion")
    assert result["adjusted_calories"] == 160.0
    print(f"  Half portion: 320kcal → {result['adjusted_calories']}kcal ✓")
    
    # Test double portion
    result = adjust_portion(320.0, 2.0, "double portion")
    assert result["adjusted_calories"] == 640.0
    print(f"  Double portion: 320kcal → {result['adjusted_calories']}kcal ✓")
    
    # Test custom multiplier
    result = adjust_portion(320.0, 0.75, "3/4 portion")
    assert result["adjusted_calories"] == 240.0
    print(f"  3/4 portion: 320kcal → {result['adjusted_calories']}kcal ✓")


def test_healthier_alternatives():
    """Test healthier alternatives"""
    print("\n✓ Testing Healthier Alternatives...")
    
    # Test pizza alternatives
    result = get_healthier_alternatives("pizza", 320.0)
    assert result["detected_food"] == "pizza"
    assert len(result["alternatives"]) > 0
    print(f"  Pizza alternatives: {len(result['alternatives'])} found ✓")
    for alt in result["alternatives"]:
        print(f"    - {alt['name']}: {alt['calories']}kcal ({alt['reduction_percent']}% less)")
    
    # Test burger alternatives
    result = get_healthier_alternatives("burger", 370.0)
    assert result["detected_food"] == "burger"
    assert len(result["alternatives"]) > 0
    print(f"  Burger alternatives: {len(result['alternatives'])} found ✓")
    
    # Test fries alternatives
    result = get_healthier_alternatives("fries", 170.0)
    assert result["detected_food"] == "fries"
    assert len(result["alternatives"]) > 0
    print(f"  Fries alternatives: {len(result['alternatives'])} found ✓")
    
    # Test food without alternatives
    result = get_healthier_alternatives("rice", 130.0)
    assert result["detected_food"] == "rice"
    assert len(result["alternatives"]) == 0
    print(f"  Rice alternatives: {len(result['alternatives'])} found (no alternatives configured) ✓")


def test_alternatives_coverage():
    """Check which foods have alternatives"""
    print("\n✓ Healthier Alternatives Coverage:")
    from app.config import HEALTHIER_ALTERNATIVES
    
    for food in sorted(HEALTHIER_ALTERNATIVES.keys()):
        count = len(HEALTHIER_ALTERNATIVES[food])
        print(f"  {food.capitalize()}: {count} alternatives")


if __name__ == "__main__":
    print("=" * 50)
    print("Testing Backend Enhancements")
    print("=" * 50)
    
    try:
        test_portion_adjustment()
        test_healthier_alternatives()
        test_alternatives_coverage()
        
        print("\n" + "=" * 50)
        print("✓ All tests passed!")
        print("=" * 50)
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
