def full_pipeline():
    players, stats = run_api()
    try:
        run_web()
    except Exception as e:
        print(f"⚠️ Web extraction skipped due to error: {e}")
    run_csv()
    run_sql()
    run_big()

    # خطوة التحويل (تطبيع/تنظيف وكتابة ملفات جاهزة)
    run_transform()

    load_postgres(players, stats)
    load_mongo(players, stats)
    print("Full ETL pipeline finished")