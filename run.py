import os
import uvicorn

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "true").lower() == "true"
    
    print("=" * 65)
    print("🏆 SPORTS HUB - 실시간 스포츠 종합 순위 & 기록 대시보드")
    print(f"👉 로컬 웹서버 접속 주소: http://{host}:{port}")
    print("⚾ KBO 야구  |  ⚽ K리그  |  🌍 해외축구  |  🧢 MLB 메이저리그")
    print("=" * 65)
    uvicorn.run("app.main:app", host=host, port=port, reload=reload)
