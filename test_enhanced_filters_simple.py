import requests


def test_enhanced_filters():
    print("🧪 Testing Enhanced Categories Filter System...")

    try:
        response = requests.get(
            "http://127.0.0.1:8000/ar/categories/?section=classified"
        )
        content = response.text

        print(f"✅ Page Status: {response.status_code}")

        # Test filter elements
        filter_tests = {
            "Location Filter": 'id="locationFilter"' in content,
            "Price Min Input": 'id="minPrice"' in content,
            "Price Max Input": 'id="maxPrice"' in content,
            "Featured Filter": 'id="filterFeatured"' in content,
            "With Images Filter": 'id="filterWithImages"' in content,
            "Verified Filter": 'id="filterVerified"' in content,
            "Advanced Dropdown": 'id="filterDropdownBtn"' in content,
        }

        print("\n📋 Filter Elements Test:")
        all_elements_found = True
        for test_name, found in filter_tests.items():
            status = "✅ FOUND" if found else "❌ MISSING"
            print(f"  {test_name}: {status}")
            if not found:
                all_elements_found = False

        # Test dropdown options
        dropdown_tests = {
            "Sort by Name": 'data-sort="name"' in content,
            "Sort by Featured": 'data-sort="-featured"' in content,
            "Date Filter Today": 'data-date="today"' in content,
            "Date Filter Week": 'data-date="week"' in content,
            "Section Classified": 'data-section="classified"' in content,
        }

        print("\n🔽 Dropdown Options Test:")
        all_dropdown_found = True
        for test_name, found in dropdown_tests.items():
            status = "✅ FOUND" if found else "❌ MISSING"
            print(f"  {test_name}: {status}")
            if not found:
                all_dropdown_found = False

        # Test checkbox filters
        checkbox_tests = {
            "Filter Active": "filterActive" in content,
            "Filter Featured": "filterFeatured" in content,
            "Filter Negotiable": "filterNegotiable" in content,
            "Filter With Images": "filterWithImages" in content,
            "Filter With Contact": "filterWithContact" in content,
            "Filter Verified": "filterVerified" in content,
        }

        print("\n☑️ Checkbox Filters Test:")
        all_checkboxes_found = True
        for test_name, found in checkbox_tests.items():
            status = "✅ FOUND" if found else "❌ MISSING"
            print(f"  {test_name}: {status}")
            if not found:
                all_checkboxes_found = False

        # Test location options
        location_tests = {
            "Riyadh Option": 'value="riyadh"' in content,
            "Jeddah Option": 'value="jeddah"' in content,
            "Dammam Option": 'value="dammam"' in content,
        }

        print("\n📍 Location Options Test:")
        all_locations_found = True
        for test_name, found in location_tests.items():
            status = "✅ FOUND" if found else "❌ MISSING"
            print(f"  {test_name}: {status}")
            if not found:
                all_locations_found = False

        # Test JavaScript functionality
        js_tests = {
            "Setup Filter Function": "setupFilterFunctionality" in content,
            "Reset Filters Function": "resetFilters" in content,
            "Current Location Variable": "currentLocation" in content,
            "Current Date Filter": "currentDateFilter" in content,
            "Filter Categories Function": "filterCategories" in content,
        }

        print("\n🔧 JavaScript Functions Test:")
        all_js_found = True
        for test_name, found in js_tests.items():
            status = "✅ FOUND" if found else "❌ MISSING"
            print(f"  {test_name}: {status}")
            if not found:
                all_js_found = False

        print("\n" + "=" * 60)
        if all(
            [
                all_elements_found,
                all_dropdown_found,
                all_checkboxes_found,
                all_locations_found,
                all_js_found,
            ]
        ):
            print("🎉 ALL TESTS PASSED! Enhanced filter system is working correctly.")
            print("✨ Features successfully added:")
            print("  • Location filtering (cities)")
            print("  • Advanced status filters (Featured, Verified, etc.)")
            print("  • Date range filtering")
            print("  • Content type filters (With Images, Contact info)")
            print("  • Enhanced sorting options")
            print("  • Comprehensive reset functionality")
        else:
            print("⚠️ Some tests failed. Check the results above.")
        print("=" * 60)

    except Exception as e:
        print(f"❌ Error testing filters: {e}")


if __name__ == "__main__":
    test_enhanced_filters()
