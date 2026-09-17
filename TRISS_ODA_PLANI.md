# TRISS — ODA PLANI (Kişisel PC Asistanı)

## HEDEF
Konuşarak yönettiğin asistan. İsmini bilir, seni anlar, ilk aşamada yazılı cevap verir, PC'de iş yapar (WhatsApp dahil).
Piyasa yok. Sadece sen (+ belki arkadaş).

---

## STACK (KİLİTLİ)

| Parça | Karar |
|--------|--------|
| Kulak | Wake word + Whisper (düzgün Türkçe) |
| Beyin A (ucuz) | Gemini Flash → sohbet + basit komut |
| Beyin B (güçlü) | Claude Sonnet → ajan / ekran / WhatsApp |
| Çıkış | Faz 0-4: Yazılı cevap, Faz 5: ElevenLabs (yedek: edge-tts) |
| Eller | Skill'ler + masaüstü otomasyon + onay |

Akış (şimdi): **Mikrofon → Anlama → Router → Model → Tool/PC → Yazı**  
Akış (son faz): **Mikrofon → Anlama → Router → Model → Tool/PC → Yazı + Ses**

---

## FAZLAR (SIRAYLA)

| Faz | Ne | Bitmiş sayılır ki |
|-----|-----|-------------------|
| **0** Stabilize (Yazılı) | Key'ler, bağımlılık, "Ben Triss", yazılı çalışır hale getir | Günaydın Triss → yazılı cevap, çökmez |
| **1** Ajan (Yazılı) | Tool'lar + 2 kademe router + onay | Müzik / Chrome / hava stabil |
| **2** Masaüstü (Yazılı) | Tıkla, yaz, pencere, ekran bak | Not Defteri aç-yaz-kaydet |
| **3** WhatsApp (Yazılı) | Kişiye yaz → onay → gönder | Gerçek mesaj gider |
| **4** Ses Kalitesi | Wake doğru, Whisper, konuşma akışı | 10 dk kullanım, isim yanlış az |
| **5** TTS + Hafif paylaşım | ElevenLabs/edge-tts + requirements + kısa README | Sesli cevap + arkadaş kurabilsin |

Sıra bozulmaz: önce yazılı çekirdek, sonra ajan, sonra PC, sonra WhatsApp, en son TTS.

---

## SENİN HAZIRLIK

- [ ] Anthropic API key
- [ ] ElevenLabs API key (+ ses seç) [Faz 5'te gerekli]
- [ ] Gemini key (zaten var — kota izle)
- [ ] Mikrofon / hoparlör
- [ ] (Sonra) WhatsApp Desktop açık

---

## KURALLAR

1. Tehlikeli işte **onay zorunlu** (şimdi yazılı, sonra sesli)
2. Şüphede **güçlü modele** çık
3. Her şeyi tek günde bitirme — faz faz
4. `.env` asla paylaşma

---

## YAPMAYACAĞIZ

Mağaza / installer / çok kullanıcı / banka otomasyonu / 5 ayrı model filoları

---

## BÜTÇE (KABA)

- Yazılı fazlarda: daha düşük (ElevenLabs maliyeti yok)
- TTS açılınca: ~$40–65/ay bandına yaklaşır (kullanıma göre)

---

## YARIN İLK İŞ

**Faz 0** — API'ler + yazılı smoke test.

Komut: `Faz 0'a başla`

---

*Son güncelleme: 30 Temmuz 2026*
