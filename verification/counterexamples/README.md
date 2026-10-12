# Danh Má»¥c Pháº£n VĂ­ Dá»¥ (Counterexamples) PhĂ¡t Hiá»‡n Qua Kiá»ƒm Chá»©ng

## 1. BMC-CE-01: Authentication Bypass (Bá» qua xĂ¡c thá»±c)
- **MĂ´ hĂ¬nh**: `verification/bmc/kiem_chung_xac_thuc_truoc_sac.py`
- **Lá»— há»•ng**: Tráº¡ng thĂ¡i chuyá»ƒn trá»±c tiáº¿p `IDLE -> CONNECTED -> CHARGING`.
- **Pháº£n vĂ­ dá»¥**: 
  - Táº¡i bÆ°á»›c $k=2$, xe á»Ÿ tráº¡ng thĂ¡i `CHARGING` vá»›i thuá»™c tĂ­nh `is_authenticated = False`.
- **Báº£n vĂ¡**: Báº¯t buá»™c má»i luá»“ng chuyá»ƒn tráº¡ng thĂ¡i sang `CHARGING` pháº£i Ä‘i qua `AUTHENTICATED` vĂ  `READY`.

## 2. SMT-CE-01: Pin VÆ°á»£t QuĂ¡ 100% SOC (Overcharge)
- **MĂ´ hĂ¬nh**: `verification/smt/kiem_chung_gioi_han_soc.py`
- **Lá»— há»•ng**: KhĂ´ng cháº·n cáº­n trĂªn khi cá»™ng nÄƒng lÆ°á»£ng náº¡p.
- **Pháº£n vĂ­ dá»¥**:
  - `current_soc = 95.0%`, `delta_soc = 10.0%` $\rightarrow$ `new_soc = 105.0% > 100%` (`SAT`).
- **Báº£n vĂ¡**: Bá»• sung hĂ m bĂ£o hĂ²a `min(100.0, current_soc + delta_soc)`. Sau khi vĂ¡: `UNSAT`.

## 3. SMT-CE-02: QuĂ¡ Táº£i CĂ´ng Suáº¥t Tráº¡m Sáº¡c (Overload)
- **MĂ´ hĂ¬nh**: `verification/smt/kiem_chung_phan_phoi_cong_suat.py`
- **Lá»— há»•ng**: Cáº£ 5 xe sáº¡c tá»± do á»Ÿ má»©c tá»‘i Ä‘a $22\text{ kW}$.
- **Pháº£n vĂ­ dá»¥**:
  - $5 \times 22\text{ kW} = 110\text{ kW} > 100\text{ kW}$ (`SAT`).
- **Báº£n vĂ¡**: Thuáº­t toĂ¡n Power Manager cĂ¢n báº±ng táº£i tráº§n $\le 20\text{ kW}$/xe. Sau khi vĂ¡: `UNSAT`.
