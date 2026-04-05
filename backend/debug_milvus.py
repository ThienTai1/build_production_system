from pymilvus import connections, utility

def test_conn():
    print("Trying to connect to Milvus...")
    try:
        connections.connect(alias="default", host="127.0.0.1", port="19530")
        print(f"✅ Success! Milvus Version: {utility.get_server_version()}")
        connections.disconnect("default")
    except Exception as e:
        print(f"❌ Failed: {e}")

if __name__ == "__main__":
    test_conn()