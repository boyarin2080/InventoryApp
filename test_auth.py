#!/usr/bin/env python
"""
Test script to verify authentication system endpoints.
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_management.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

def test_authentication_urls():
    """Test authentication URLs are accessible."""
    client = Client()
    
    print("Testing authentication URLs...")
    
    # Test login page
    response = client.get(reverse('authentication:login'))
    print(f"Login page status: {response.status_code} (expected: 200)")
    assert response.status_code == 200, f"Login page returned {response.status_code}"
    
    # Test logout page (should show logout confirmation if not authenticated)
    response = client.get(reverse('authentication:logout'))
    print(f"Logout page (unauthenticated) status: {response.status_code} (expected: 200)")
    assert response.status_code == 200, f"Logout page returned {response.status_code}"
    
    # Test dashboard (should redirect to login if not authenticated)
    response = client.get(reverse('dashboard'))
    print(f"Dashboard (unauthenticated) status: {response.status_code} (expected: 302 redirect to login)")
    assert response.status_code == 302, f"Dashboard returned {response.status_code}"
    
    # Test login with valid credentials
    print("\nTesting login with valid credentials...")
    response = client.post(reverse('authentication:login'), {
        'username': 'testuser',
        'password': 'test123',
    })
    print(f"Login POST status: {response.status_code} (expected: 302 redirect to dashboard)")
    assert response.status_code == 302, f"Login POST returned {response.status_code}"
    
    # Now test authenticated access
    print("\nTesting authenticated access...")
    response = client.get(reverse('dashboard'))
    print(f"Dashboard (authenticated) status: {response.status_code} (expected: 200)")
    assert response.status_code == 200, f"Dashboard returned {response.status_code}"
    
    # Test authenticated logout page
    response = client.get(reverse('authentication:logout'))
    print(f"Logout page (authenticated) status: {response.status_code} (expected: 200)")
    assert response.status_code == 200, f"Logout page returned {response.status_code}"
    
    # Test logout
    print("\nTesting logout...")
    response = client.post(reverse('authentication:logout'))
    print(f"Logout POST status: {response.status_code} (expected: 302 redirect to login)")
    assert response.status_code == 302, f"Logout POST returned {response.status_code}"
    
    print("\n✅ All authentication tests passed!")

def test_template_responses():
    """Test that templates are being rendered correctly."""
    client = Client()
    
    print("\nTesting template rendering...")
    
    # Test login template
    response = client.get(reverse('authentication:login'))
    assert 'Login - Inventory Management System' in str(response.content)
    assert '<form method="post"' in str(response.content)
    print("✅ Login template renders correctly")
    
    # Test authenticated dashboard
    client.login(username='testuser', password='test123')
    response = client.get(reverse('dashboard'))
    assert 'Dashboard - Inventory Management System' in str(response.content)
    assert 'Welcome back, testuser!' in str(response.content)
    assert 'navbar' in str(response.content)
    print("✅ Dashboard template renders correctly")
    
    # Test logout template
    response = client.get(reverse('authentication:logout'))
    assert 'Logout - Inventory Management System' in str(response.content)
    assert 'Are you sure you want to logout?' in str(response.content)
    print("✅ Logout template renders correctly")

def main():
    """Run all tests."""
    try:
        test_authentication_urls()
        test_template_responses()
        print("\n🎉 All tests completed successfully!")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()