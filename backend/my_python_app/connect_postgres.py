import psycopg2

try:
    conn = psycopg2.connect(
        dbname="your_database",
        user="postgres",
        password="your_password",
        host="pgsql_container",
        port="5432"
    )

    cur = conn.cursor()

    # 查詢指定資料表的欄位資訊
    table_name = "users"
#    cur.execute(f"""
#        SELECT column_name, data_type 
#        FROM information_schema.columns 
#        WHERE table_name = '{table_name}';
#    """)

#    print(f"\n📌 資料表 `{table_name}` 的欄位資訊：")
#    for column in cur.fetchall():
#        print(f"🔹 欄位名稱: {column[0]}, 資料類型: {column[1]}")

    # 查詢該資料表的所有資料
    cur.execute(f"SELECT * FROM {table_name};")
    rows = cur.fetchall()

    # 顯示資料
    for row in rows:
        print(row)

    cur.close()
    conn.close()

except Exception as e:
    print("❌ 無法連接 PostgreSQL:", e)
