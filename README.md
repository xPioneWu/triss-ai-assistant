# ✨ Triss — Kişisel Sesli AI Asistan

Türkçe konuşan, wake-word ile açılıp kapanan, Windows masaüstü AI asistanı.

---

## 🚀 Hızlı Başlangıç

### 1. Python Kurulumu
Python 3.10+ gereklidir. [python.org](https://python.org) adresinden indirin.

### 2. Kurulum Sihirbazını Çalıştırın
```bash
cd triss
python setup.py
```
Sihirbaz sizi adım adım yönlendirecek:
- Gerekli paketleri yükleyecek
- API anahtarlarınızı toplayacak
- Mikrofon ve ses testleri yapacak

### 3. Triss'i Başlatın
```bash
python main.py
```

### 4. Kullanım
| Söz | Eylem |
|-----|-------|
| `"Günaydın Triss"` | Triss uyanır 🟢 |
| `"İyi Geceler Triss"` | Triss uyur 🔴 |
| `"Hava nasıl?"` | İstanbul hava durumu |
| `"İstanbul'da hava nasıl?"` | Şehir hava durumu |
| `"Imagine Dragons çal"` | Spotify'da çalar |
| `"Müziği durdur"` | Spotify durur |
| `"Sonraki şarkı"` | Sonraki parça |
| `"Chrome'u aç"` | Tarayıcı açar |
| `"Python nedir?"` | Sohbet / bilgi |

---

## 🔑 API Anahtarları

### Anthropic (ZORUNLU)
1. [console.anthropic.com](https://console.anthropic.com) → Kayıt ol
2. **API Keys** → **Create Key**
3. `.env` dosyasına yapıştır: `ANTHROPIC_API_KEY=sk-ant-...`

### OpenWeatherMap (hava durumu)
1. [openweathermap.org/api](https://openweathermap.org/api) → Ücretsiz kayıt
2. **API Keys** sekmesi → key kopyala
3. `.env`: `OPENWEATHER_API_KEY=...`

### Spotify (müzik kontrolü)
1. [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard) → **Create App**
2. App adı: `Triss`, Redirect URI: `http://localhost:8888/callback`
3. **Settings** → Client ID ve Secret'ı kopyala
4. `.env`:
   ```
   SPOTIFY_CLIENT_ID=...
   SPOTIFY_CLIENT_SECRET=...
   ```
5. İlk çalıştırmada tarayıcıda Spotify oturum açma sayfası açılacak — onaylayın.

---

## 📁 Dosya Yapısı

```
triss/
├── main.py           # Ana döngü
├── triss_core.py     # Beyin: wake word + Claude API + skill yönlendirme
├── voice_output.py   # TTS: Türkçe kadın sesi (edge-tts)
├── env_loader.py     # .env yükleyici
├── setup.py          # Kurulum sihirbazı
├── .env              # API anahtarları (git'e EKLEMEYİN!)
├── memory.json       # Konuşma hafızası (otomatik oluşur)
├── triss.log         # Uygulama logları
└── skills/
    ├── weather.py    # Hava durumu
    ├── music.py      # Spotify kontrolü
    └── system.py     # Uygulama açma / web arama
```

---

## ⚙️ Ses Tanıma Seçenekleri

| Yöntem | Kalite | İnternet | Kurulum |
|--------|--------|----------|---------|
| **Whisper** (önerilen) | ⭐⭐⭐⭐⭐ | Hayır (local) | `pip install openai-whisper` |
| **Google STT** | ⭐⭐⭐⭐ | Evet | Otomatik (fallback) |

Whisper yüklüyse otomatik kullanılır. Yoksa Google STT devreye girer.

---

## 🛠️ Sorun Giderme

**PyAudio kurulamıyor:**
```bash
pip install pipwin
pipwin install pyaudio
```

**"Aktif Spotify cihazı bulunamadı":**
Spotify uygulamasını açın ve bir şarkı başlatıp durdurun — cihaz aktif hale gelir.

**Türkçe karakterler bozuk görünüyor:**
Terminal kodlamasını UTF-8 yapın:
```bash
chcp 65001
```

**Mikrofon tanınmıyor:**
```python
import speech_recognition as sr
print(sr.Microphone.list_microphone_names())
```
Çıktıdan doğru mikrofon indeksini bulun ve `triss_core.py`'de `sr.Microphone(device_index=N)` olarak ayarlayın.

---

## 🔒 Güvenlik

- `.env` dosyasını asla GitHub'a yüklemeyin
- Proje dizininde bir `.gitignore` oluşturun:
  ```
  .env
  .spotify_cache
  memory.json
  triss.log
  __pycache__/
  ```

---

## 📈 Yeni Skill Eklemek

`skills/` klasörüne yeni bir `.py` dosyası oluşturun ve `triss_core.py`'deki `_execute_skill` metoduna yeni action ekleyin. Sistem prompt'unu da güncelleyin.

---

*Triss, Claude Sonnet ile güçlendirilmiştir.*
