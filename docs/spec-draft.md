# SPEC — AI Product Hackathon

**Nhóm:** Team 31, E403, Đăng Thanh Tùng (dang1412), Trần Kiên Trường (tktrev), Trịnh Ngọc Tú (cheeka13), Đặng Quang Minh (minh267), Trần Tiến Long (longtranvie)
**Track:** ☑ XanhSM · ☐ VinFast · ☐ Vinmec · ☐ VinUni-VinSchool · ☐ Open
**Problem statement (1 câu):** Người dùng VinBus mất thời gian tìm tuyến bus tối ưu trên ứng dụng vì giao diện bản đồ phức tạp — AI chatbot trả lời bằng ngôn ngữ tự nhiên, gợi ý tuyến bus phù hợp trong vài giây.

---

## 1. AI Product Canvas

|   | Value | Trust | Feasibility |
|---|-------|-------|-------------|
| **Câu hỏi** | User nào? Pain gì? AI giải gì? | Khi AI sai thì sao? User sửa bằng cách nào? | Cost/latency bao nhiêu? Risk chính? |
| **Trả lời** | - User: 2 nhóm — (1) commuters đi bus hàng ngày muốn route nhanh, (2) tourists/người lần đầu không biết tuyến nào<br>- Pain: Giao diện bản đồ VinBus khó dùng, phải tap nhiều bước để tìm tuyến, không biết chỗ lên/xuống<br>- AI giải: Chat tự nhiên "đi từ A đến B" → gợi tuyến bus cụ thể, trạm dừng, giờ tàu, giá vé | - AI sai route → user thấy ngay (so sánh với kinh nghiệm hoặc map), tap "Sai tuyến" → log correction + gợi tuyến thay thế<br>- Nếu AI không biết → nói "tôi chưa có dữ liệu tuyến này" thay vì hallucinate<br>- Feedback loop: corrections đi vào bảng để cải thiện prompt/engine | - Cost: ~$0.01-0.03/query (Claude Haiku), ~$0.10-0.15/query (Sonnet)<br>- Latency: target <3s end-to-end<br>- Risk chính: Hallucinate tuyến bus không tồn tại → user đi sai đường, mất niềm tin<br>- Mitigation: Luôn validate route against known route DB, show confidence score |

**Automation hay augmentation?** ☑ Augmentation · ☐ Automation
Justify: User vẫn cầm quyết định — AI gợi ý, user xác nhận hoặc từ chối. Cost of reject = 0. Không tự động booking hay payment.

**Learning signal:**

1. **User correction đi vào đâu?** Bảng `correction_log` trong database: `{query, suggested_route, user_correction, timestamp, user_id}`. Dùng để analyze errors và improve prompt.
2. **Product thu signal gì để biết tốt lên hay tệ đi?** (a) % queries có user tap "Sai tuyến" (target <10%), (b) session length (user quay lại dùng lại không?), (c) NPS/satisfaction survey sau mỗi 10 queries
3. **Data thuộc loại nào?** ☐ User-specific · ☑ Domain-specific · ☑ Real-time · ☐ Human-judgment · ☑ Khác: Route/GTFS data
   Có marginal value không? Model foundation (Claude) đã biết location names ở VN nhưng **không biết VinBus routes cụ thể** — data này là competitive advantage cần thu thập.

---

## 2. User Stories — 4 paths

### Feature: Chat-based Route Query

**Trigger:** User nhập câu hỏi bằng tiếng Việt (hoặc tiếng Anh) vào chatbox — "Tôi muốn đi từ Landmark 81 về Quận 1", "How do I get to Ben Thanh market?", "Đi từ Vinhomes Golden River về trung tâm"

| Path | Câu hỏi thiết kế | Mô tả |
|------|-------------------|-------|
| Happy — AI đúng, tự tin | User thấy gì? Flow kết thúc ra sao? | Bot reply: "Tuyến **Bus 12** đi từ **Landmark 81** → **Bến Thành** → **Quận 1**<br>⏱ 25 phút · 💰 7,000 VND · 🚌 2 trạm dừng<br>User thấy đúng → có thể "Bắt đầu navigation" hoặc hỏi tiếp. Kết thúc flow. |
| Low-confidence — AI không chắc | System báo "không chắc" bằng cách nào? User quyết thế nào? | Bot: "Tôi tìm được 2 tuyến có thể phù hợp:<br>① Bus 12 (phổ biến, 25 phút)<br>② Bus 56 (ít trung chuyển, 35 phút)<br>Bạn muốn chọn tuyến nào?" — Show 2 options + giải thích khác biệt. User chọn 1. |
| Failure — AI sai | User biết AI sai bằng cách nào? Recover ra sao? | Bot gợi tuyến Bus 12 nhưng Landmark 81 không có trạm Bus 12 gần đó.<br>→ User thấy trong thực tế → tap "Sai tuyến" → Bot: "Xin lỗi, tôi sẽ ghi nhận. Bạn có thể cho tôi biết trạm gần nhất với bạn không?" → thu thập thông tin để cải thiện. |
| Correction — user sửa | User sửa bằng cách nào? Data đó đi vào đâu? | User tap "Sai tuyến" hoặc reply "Không phải, tôi muốn đi từ trạm # khác"<br>→ Correction logged: `{query, bot_suggestion, user_correction, route_corrected_to}`<br>→ Dùng để analyze patterns, improve distance-to-route matching logic |

### Feature (optional/phase 2): Live Bus Tracking Query

**Trigger:** User hỏi "Bus 12 còn bao lâu nữa?" hoặc "Tàu 15 đến chưa?"

| Path | Câu hỏi thiết kế | Mô tả |
|------|-------------------|-------|
| Happy — AI đúng, tự tin | User thấy gì? | Bot: "Bus 12 của bạn đang đến trạm **Bến Thành** — dự kiến **3 phút** nữa. Tàu kế tiếp lúc 14:35." |
| Low-confidence — AI không chắc | System báo "không chắc" bằng cách nào? | Bot: "Tôi không có dữ liệu real-time cho tuyến này lúc này. Bạn có thể kiểm tra trên bản đồ chính của app?" |
| Failure — AI sai | User biết AI sai bằng cách nào? | User thấy bus đã qua trạm nhưng bot nói còn 5 phút → "Báo cáo sai" → log feedback |
| Correction — user sửa | User sửa bằng cách nào? | "Báo cáo sai" → log vào `tracking_feedback` |

---

## 3. Eval metrics + threshold

**Optimize precision hay recall?** ☑ Precision · ☐ Recall
**Tại sao?** Người dùng đang di chuyển — nếu AI gợi sai tuyến (precision thấp), họ đi lạc hoặc muộn, mất niềm tin ngay. Recall thấp = user hỏi lại hoặc tự tìm, không gây hại trực tiếp. **Precision quan trọng hơn.**

**Nếu sai ngược lại thì chuyện gì xảy ra?** Nếu optimize recall (high recall, low precision) → AI gợi nhiều tuyến nhưng nhiều tuyến sai → user không biết tin cái nào → bypass chatbot → product thất bại.

| Metric | Threshold | Red flag (dừng khi) |
|--------|-----------|---------------------|
| Route accuracy — AI gợi tuyến đúng bao nhiêu % | ≥80% | <65% trong 1 tuần |
| User satisfaction (1-5 sao) | ≥4.0 | <3.0 trong 1 tuần |
| Correction rate — % queries bị user sửa | <10% | >20% |
| Latency p95 (time to first token) | <3s | >5s |
| Fallback rate — % queries phải fallback do low confidence | <15% | >30% |

---

## 4. Top 3 failure modes

*Liệt kê cách product có thể fail — không phải list features.*
*"Failure mode nào user KHÔNG BIẾT bị sai? Đó là cái nguy hiểm nhất."*

| # | Trigger | Hậu quả | Mitigation |
|---|---------|---------|------------|
| 1 | **Hallucinate tuyến bus không tồn tại** — AI "tự tin" gợi Bus 99 đi tuyến XYZ nhưng VinBus không có tuyến này | User đi sai đường, có thể đến trạm chờ 20 phút mới biết bus không đến. **User không biết bị sai** cho đến khi trải nghiệm thực tế. Reputational damage nghiêm trọng. | (1) Luôn validate gợi ý against route database trước khi reply. (2) Nếu route không match → "Tôi không có dữ liệu tuyến này" thay vì invent. (3) Show confidence: "Tuyến này dựa trên dữ liệu cũ, bạn nên kiểm tra lại" |
| 2 | **Ambiguous location names** — User nói "đi về nhà" hoặc "về công ty" → AI không resolve được địa điểm cụ thể | AI hỏi lại clarification → user frustrated → abandon conversation | (1) Prompt phải handle ambiguity rõ: "Bạn muốn đi từ đâu?" thay vì guess. (2) Support saved locations (home/work) nếu user đã login. (3) Suggest nearby landmarks khi không resolve được |
| 3 | **Out-of-date route data** — VinBus thay đổi tuyến nhưng LLM vẫn gợi tuyến cũ | User đi tuyến không còn hoạt động. **User không biết bị sai** vì không có real-time verification | (1) Datasource phải là GTFS data mới nhất, auto-refresh. (2) AI response phải có disclaimer: "Thông tin dựa trên dữ liệu [date], kiểm tra app chính thức để confirm". (3) User reports route changes → feedback pipeline |

---

## 5. ROI 3 kịch bản

|   | Conservative | Realistic | Optimistic |
|---|-------------|-----------|------------|
| **Assumption** | 50 user/ngày (hackathon demo) | 500 user/ngày sau 1 tháng deploy | 5,000 user/ngày, 10% dùng chat |
| **Cost** | $2/ngày (50 queries × $0.04) | $20/ngày (500 queries × $0.04) | $200/ngày (5,000 queries × $0.04) |
| **Benefit** | Validation for demo + learning | Giảm 30% support tickets về route query (~50 tickets/ngày saved × $2/ticket = $100/ngày) | Tăng app retention 10%, reduce map-only users |
| **Net** | -$2/ngày (cost < meaningful benefit yet) | +$80/ngày | + tùy conversion uplift |
| **Humane cost (benevolent)** | Không có | 50 commuters tiết kiệm 2-3 min/query × 500 = ~17h/ngày collective time saved | 500 commuters × 2 min = ~17h/ngày + better UX satisfaction |

**Kill criteria:** (a) Cost > Benefit 2 tuần liên tục ở Realistic scenario, (b) Correction rate >20% persist sau 2 tuần optimization attempts, (c) Negative NPS <-2 (thay vì just kill, nên debug trước)

---

## 6. Mini AI spec (1 trang)

**Product:** VinBus Route Chatbot — giao diện hội thoại giúp user tìm tuyến bus tối ưu bằng ngôn ngữ tự nhiên (tiếng Việt/trả lời bằng tiếng Việt, có hỗ trợ tiếng Anh cho tourists).

**Cho ai:** Mixed — (1) commuters đi bus hàng ngày muốn route nhanh mà không cần mở bản đồ, (2) tourists/người mới ở TP.HCM/Hà Nội chưa biết tuyến bus nào phù hợp.

**AI làm gì (auto/aug):** Augmentation — AI gợi ý tuyến bus, user xác nhận hoặc từ chối. AI không book, không thanh toán. User vẫn control quyết định.

**Quality (precision/recall):** Prioritize **precision** (≥80% route accuracy). Nếu không chắc → hỏi clarification hoặc show 2 options. Không bao giờ hallucinate tuyến không tồn tại.

**Risk chính:**
1. Hallucinate route → user đi lạc → mitigation: validate against route DB, show confidence
2. Ambiguous location → AI guess sai → mitigation: ask clarification, support saved locations
3. Out-of-date data → AI dùng route cũ → mitigation: GTFS auto-refresh, add disclaimer

**Data flywheel:** User corrections → `correction_log` table → weekly analysis → improve prompt + route matching logic. Không retrain model, chỉ improve prompt và RAG context. Marginal value: VinBus route data là proprietary, model foundation không có → data là competitive advantage.

**Technical approach:** Claude API (Haiku cho cost-efficiency, Sonnet cho complex queries) + route DB (GTFS format) + Next.js frontend. Function calling để extract `{origin, destination, time?, preferences?}` từ natural language → query route DB → format response với route details + map link.
