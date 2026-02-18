#!/usr/bin/env python
"""
Test Redis connectivity for local development
Run with: poetry run python test_redis.py
"""

import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "idrissimart.settings.local")

import django
django.setup()

from django.conf import settings


def test_redis_connection():
    """Test basic Redis connection"""
    print("=" * 60)
    print("Testing Redis Connection for Local Development")
    print("=" * 60)

    try:
        import redis
        print("\n✅ Redis library imported successfully")
    except ImportError:
        print("\n❌ Redis library not found. Install with: poetry add redis")
        return False

    # Test basic Redis connection
    try:
        r = redis.Redis(host='127.0.0.1', port=6379, db=0)
        response = r.ping()
        if response:
            print("✅ Redis server is running and responding to PING")

            # Get Redis info
            info = r.info()
            print(f"✅ Redis version: {info['redis_version']}")
            print(f"✅ Redis mode: {info['redis_mode']}")
            print(f"✅ Connected clients: {info['connected_clients']}")

            # Test set/get
            r.set('test_key', 'Hello from Django!')
            value = r.get('test_key')
            print(f"✅ Test key set and retrieved: {value.decode('utf-8')}")
            r.delete('test_key')

            return True
        else:
            print("❌ Redis server not responding")
            return False

    except redis.ConnectionError as e:
        print(f"❌ Cannot connect to Redis: {e}")
        print("\nMake sure Redis is running:")
        print("  sudo service redis-server start")
        print("  redis-cli ping")
        return False
    except Exception as e:
        print(f"❌ Error connecting to Redis: {e}")
        return False


def test_django_q_config():
    """Test Django-Q configuration"""
    print("\n" + "=" * 60)
    print("Testing Django-Q Configuration")
    print("=" * 60)

    try:
        q_cluster = settings.Q_CLUSTER
        print(f"\n✅ Q_CLUSTER configured: {q_cluster['name']}")
        print(f"✅ Workers: {q_cluster['workers']}")
        print(f"✅ Redis host: {q_cluster['redis']['host']}")
        print(f"✅ Redis port: {q_cluster['redis']['port']}")
        print(f"✅ Redis db: {q_cluster['redis']['db']}")
        return True
    except AttributeError:
        print("❌ Q_CLUSTER not configured in settings")
        return False
    except Exception as e:
        print(f"❌ Error checking Q_CLUSTER: {e}")
        return False


def test_channels_config():
    """Test Django Channels configuration"""
    print("\n" + "=" * 60)
    print("Testing Django Channels Configuration")
    print("=" * 60)

    try:
        channel_layers = settings.CHANNEL_LAYERS
        backend = channel_layers['default']['BACKEND']
        hosts = channel_layers['default']['CONFIG']['hosts']

        print(f"\n✅ CHANNEL_LAYERS configured")
        print(f"✅ Backend: {backend}")
        print(f"✅ Redis hosts: {hosts}")

        # Test channels connection
        from channels.layers import get_channel_layer
        import asyncio

        channel_layer = get_channel_layer()

        async def test_send():
            await channel_layer.send('test_channel', {
                'type': 'test.message',
                'text': 'Hello Channels!'
            })
            return True

        result = asyncio.run(test_send())
        if result:
            print("✅ Successfully sent test message to channel layer")

        return True

    except AttributeError:
        print("❌ CHANNEL_LAYERS not configured in settings")
        return False
    except Exception as e:
        print(f"❌ Error testing channels: {e}")
        return False


def main():
    print("\n🔴 Redis Connection Test for Local Development\n")

    results = []

    # Test Redis connection
    results.append(("Redis Connection", test_redis_connection()))

    # Test Django-Q config
    results.append(("Django-Q Config", test_django_q_config()))

    # Test Channels config
    results.append(("Channels Config", test_channels_config()))

    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    all_passed = all(result for _, result in results)

    if all_passed:
        print("\n✅ All tests passed! Redis is ready for local development.")
        print("\nYou can now run:")
        print("  - poetry run python manage.py qcluster")
        print("  - poetry run daphne idrissimart.asgi:application")
        print("\nOr use PyCharm run configurations:")
        print("  - Django Q Cluster")
        print("  - Daphne ASGI Server")
        print("  - All Services (Compound)")
        return 0
    else:
        print("\n❌ Some tests failed. Please fix the issues above.")
        print("\nQuick fixes:")
        print("  1. Install Redis: sudo apt install redis-server -y")
        print("  2. Start Redis: sudo service redis-server start")
        print("  3. Verify Redis: redis-cli ping")
        print("\nSee REDIS_LOCAL_SETUP.md for detailed setup instructions.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

