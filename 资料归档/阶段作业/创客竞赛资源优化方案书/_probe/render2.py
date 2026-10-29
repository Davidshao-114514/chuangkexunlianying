
import pymupdf, os
BASE = r"C:\Users\35464\Desktop\创客训练营\创客竞赛资源优化方案书"
d = pymupdf.open(os.path.join(BASE, "1班C组—仿真跑不队—创客竞赛资源优化方案书.pdf"))
for n in (6, 7, 13, 16, 18, 20, 26):
    d[n-1].get_pixmap(dpi=105).save(os.path.join(BASE, "_probe", "pages", f"q{n:02d}.png"))
print("ok")
