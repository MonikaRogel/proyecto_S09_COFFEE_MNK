@"
import pymysql

host = "centerbeam.proxy.rlwy.net"
port = 10485
user = "root"
password = "szMZkSJLZRTVbGaV0iyMyzfXRESrROuB"
database = "railway"

try:
    connection = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database
    )
    print("✅ Conexión exitosa a MySQL en Railway!")
    connection.close()
except Exception as e:
    print(f"❌ Error de conexión: {e}")
"@ | Out-File -FilePath test_conexion.py -Encoding utf8