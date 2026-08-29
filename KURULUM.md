# Kurulum

## 1. Repoyu ac

GitHub'da **`bushushow`** adinda (kullanici adinla birebir ayni) yeni bir **public** repo olustur.
README ekleme secenegini isaretleme, bos birakabilirsin.

## 2. Bu klasoru iceri kopyala

```bash
cd gh-profile
git init
git add .
git commit -m "feat: animated profile readme"
git branch -M main
git remote add origin https://github.com/bushushow/bushushow.git
git push -u origin main
```

Push bittiginde github.com/bushushow adresinde profil sayfanda gorunur.

## 3. Isi haritasini gercek veriyle doldur

Depodaki `assets/heatmap.svg` su an **ornek veriyle** uretildi (bu ortamdan GitHub'a
erisim kapali oldugu icin). Gercegini uretmek icin:

- **Actions** sekmesine gir → `refresh profile heatmap` → **Run workflow**.

Workflow her calistiginda `assets/heatmap.svg` dosyasini gercek katki verinle
yeniden uretip commit'ler. Sonrasinda her gun 06:17'de (TR saati) kendi kendine calisir.

Actions ilk kez calismiyorsa: **Settings → Actions → General → Workflow permissions**
altinda "Read and write permissions" secili olmali.

## 4. Icerigi kendine gore duzenle

| Ne | Nerede |
|---|---|
| Bilgi kartindaki satirlar | `scripts/make_card.py` icindeki `CONFIG` |
| Teknoloji rozetleri | `scripts/make_stack.py` icindeki `GROUPS` |
| Renkler | her scriptin basindaki `THEME` / `SCALE` |
| LinkedIn ve mail linkleri | `README.md` en altta `YOUR-LINKEDIN`, `YOUR-MAIL` |

En kolay yol: dosyayi github.com uzerinde duzenle. Repoda dosyaya gir, sag ustteki
kalem simgesine bas, degistir, "Commit changes" de. GitHub Actions degisikligi gorup
SVG'leri kendisi yeniden uretip commit'liyor; bir dakika sonra profilin guncellenmis olur.

Bilgisayarindan yapmak istersen scripti kendin calistirip cikan SVG'yi commit'le:

```bash
pip install -r requirements.txt
python scripts/make_card.py
python scripts/make_stack.py
```

## 5. Portreyi degistirmek istersen

Portre uretimi agir bagimliliklar istiyor, o yuzden ayri dosyada:

```bash
pip install -r requirements-portrait.txt
python scripts/make_ascii.py \
  --src assets/avatar.png \
  --no-invert --cols 96 --clahe 1.7 --detail 0 --gamma 0.7 --contrast 0.45 \
  --out assets/portrait.svg
```

Onemli ayarlar:

- `--src` -> kaynak fotograf. Arka plan otomatik siliniyor, sonra siluetin
  sinir kutusuna kirpiliyor, yani kadraji senin onceden ayarlaman gerekmiyor.
- `--cols` -> ASCII genisligi. Buyuttukce yuz detayi artar, SVG uzar.
- `--no-invert` -> aydinlik alanlar yogun karakterle cizilir. Isikli portreler
  icin dogru olan bu; koyu kiyafetli tam boy fotograflarda bu bayragi kaldirip
  siluet moduna gecebilirsin.
- `--gamma` (1'in altinda = daha parlak) ve `--contrast` (0-1) ton dengesi.
- `--clahe` yerel kontrast; 3'un uzerinde gurultu basliyor.
- `--detail` kumas dokusu; 0 temiz, 0.4 civari cok gurultulu.
- `--crop l,t,r,b` -> istersen kaynak fotografi onceden kirpar (piksel).

Script urettigi ASCII'yi terminale de basar, once oraya bakip ayar yapabilirsin.

## Neden hepsi SVG?

GitHub README'de JavaScript ve harici CSS calismaz. Bu yuzden animasyonlar
SVG'nin kendi icindeki SMIL etiketleriyle (`<animate>`) yazildi; hicbir harici
kaynaga bagli degil, dosyayi acan her yerde ayni sekilde oynar.
