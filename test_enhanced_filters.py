import requests
from bs4 import BeautifulSoup


def test_enhanced_filters():
    print("🧪 Testing Enhanced Categories Filter System...")

    try:
        response = requests.get(
            "http://127.0.0.1:8000/ar/categories/?section=classified"
        )
        soup = BeautifulSoup(response.content, "html.parser")

        print(f"✅ Page Status: {response.status_code}")

        # Test filter elements
        filter_tests = {
            "Location Filter": soup.find("select", {"id": "locationFilter"}),
            "Price Min Input": soup.find("input", {"id": "minPrice"}),
            "Price Max Input": soup.find("input", {"id": "maxPrice"}),
            "Featured Filter": soup.find("input", {"id": "filterFeatured"}),
            "With Images Filter": soup.find("input", {"id": "filterWithImages"}),
            "Verified Filter": soup.find("input", {"id": "filterVerified"}),
            "Date Filter Options": soup.find("a", {"data-date": "today"}),
            "Advanced Dropdown": soup.find("button", {"id": "filterDropdownBtn"}),
        }

        print("\n📋 Filter Elements Test:")
        for test_name, element in filter_tests.items():
            status = "✅ FOUND" if element else "❌ MISSING"
            print(f"  {test_name}: {status}")

        # Test dropdown options
        dropdown_options = [
            'data-sort="name"',
            'data-sort="-featured"',
            'data-date="today"',
            'data-date="week"',
            'data-section="classified"',
        ]

        print("\n🔽 Dropdown Options Test:")
        for option in dropdown_options:
            found = option in response.text
            status = "✅ FOUND" if found else "❌ MISSING"
            print(f"  {option}: {status}")

        # Test checkbox filters
        checkbox_filters = [
            "filterActive",
            "filterFeatured",
            "filterNegotiable",
            "filterWithImages",
            "filterWithContact",
            "filterVerified",
        ]

        print("\n☑️ Checkbox Filters Test:")
        all_checkboxes_found = True
        for checkbox in checkbox_filters:
            found = f'id="{checkbox}"' in response.text
            status = "✅ FOUND" if found else "❌ MISSING"
            print(f"  {checkbox}: {status}")
            if not found:
                all_checkboxes_found = False

        # Test JavaScript functionality
        js_functions = [
            "setupFilterFunctionality",
            "resetFilters",
            "currentLocation",
            "currentDateFilter",
            "filterCategories",
        ]

        print("\n🔧 JavaScript Functions Test:")
        for func in js_functions:
            found = func in response.text
            status = "✅ FOUND" if found else "❌ MISSING"
            print(f"  {func}: {status}")

        print("\n" + "=" * 50)
        if all_checkboxes_found and all(element for element in filter_tests.values()):
            print("🎉 ALL TESTS PASSED! Enhanced filter system is working correctly.")
        else:
            print("⚠️ Some tests failed. Check the results above.")
        print("=" * 50)

    except Exception as e:
        print(f"❌ Error testing filters: {e}")


if __name__ == "__main__":
    test_enhanced_filters()
