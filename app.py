import streamlit as st
from concurrent.futures import ThreadPoolExecutor
from analyzer import analyze_symptoms
from video_service import get_video_url_for_disease

st.set_page_config(
    page_title="Medical AI Assistant (தமிழ் / English)",
    page_icon="🩺",
    layout="wide"
)

# Header & Language Choice
top_col1, top_col2 = st.columns([3, 1])
with top_col1:
    st.title("🩺 AI மருத்துவ உதவியாளர் / Medical AI Assistant")
    st.write("அறிகுறிகள் அல்லது மருத்துவக் கேள்விகளை உள்ளிடுங்கள் — உடனடி விளக்கம் மற்றும் வீடியோவை தமிழில் பெறுங்கள்.")
with top_col2:
    language = st.selectbox("🌐 மொழி / Language:", ["Tamil (தமிழ்)", "English"])

is_tamil = "Tamil" in language
lang_code = "Tamil" if is_tamil else "English"

# Quick Sample Buttons
st.markdown("**மாதிரிகள் / Quick Examples:**")
q1, q2, q3 = st.columns(3)
preset_text = ""

if is_tamil:
    if q1.button("🔥 நெஞ்செரிச்சல் (Acid Reflux)"):
        preset_text = "சாப்பிட்ட பிறகு நெஞ்சில் கடுமையான எரிச்சல் மற்றும் புளித்த ஏப்பம் வருகிறது. என்ன காரணம்?"
    if q2.button("❓ காய்ச்சல் வந்தால் என்ன சாப்பிட வேண்டும்?"):
        preset_text = "காய்ச்சல் மற்றும் உடல் வலி இருக்கும்போது என்ன உணவுகள் சாப்பிட வேண்டும்?"
    if q3.button("⚡ ஒற்றைத் தலைவலி (Migraine)"):
        preset_text = "தலையின் ஒரு பகுதியில் தாங்க முடியாத வலி, குமட்டல் மற்றும் வெளிச்சம் பார்த்தால் கண் கூசுகிறது."
else:
    if q1.button("🔥 Heartburn / Acid Reflux"):
        preset_text = "Burning pain behind breastbone after meals and acid regurgitation. What causes this?"
    if q2.button("❓ What to eat during a fever?"):
        preset_text = "What are the best foods and hydration tips to recover quickly from a fever?"
    if q3.button("⚡ Throbbing Migraine"):
        preset_text = "Severe throbbing headache on one side with nausea and sensitivity to light."

# Input Box
input_label = "அறிகுறிகள் அல்லது உங்கள் மருத்துவக் கேள்வியை தட்டச்சு செய்யவும்:" if is_tamil else "Enter symptoms OR ask any medical / health question:"
user_query = st.text_area(
    input_label,
    value=preset_text,
    placeholder="உதாரணம்: எனக்கு நெஞ்சு எரியுது / இரத்த அழுத்தத்தை எப்படி குறைப்பது? / தலைவலி ஏன் வருகிறது?" if is_tamil else "e.g. Burning in chest / How to lower blood pressure naturally? / Why do we get headaches?",
    height=110
)

btn_label = "🔍 பதில் & வீடியோவை காண்க" if is_tamil else "🔍 Get Answer & Video"

if st.button(btn_label, type="primary"):
    if not user_query.strip():
        st.warning("தயவுசெய்து ஏதேனும் கேள்வியை அல்லது அறிகுறிகளை உள்ளிடவும்." if is_tamil else "Please enter your question or symptoms first.")
    else:
        with st.spinner("விளக்கம் மற்றும் வீடியோ தயாராகிறது (Searching AI & Video in parallel)..." if is_tamil else "Analyzing query and searching video in parallel..."):
            
            # RUN IN PARALLEL: AI Analysis & YouTube Search run simultaneously!
            with ThreadPoolExecutor(max_workers=2) as executor:
                ai_future = executor.submit(analyze_symptoms, user_query, lang_code)
                video_future = executor.submit(get_video_url_for_disease, user_query, lang_code)

                result = ai_future.result()
                video_url = video_future.result()

            # Emergency Alert
            if result.is_emergency:
                st.error(f"🚨 **அவசர எச்சரிக்கை / EMERGENCY WARNING**: {result.emergency_warning}")
                st.stop()

            # Heading Badge
            display_title = f"{result.title_ta} ({result.title_en})" if is_tamil else f"{result.title_en}"
            badge_text = "அறிகுறி பகுப்பாய்வு" if result.is_symptom_diagnosis else "மருத்துவ விளக்கம்"
            if not is_tamil:
                badge_text = "Symptom Diagnosis" if result.is_symptom_diagnosis else "Medical Explanation"
            
            st.success(f"📌 **{badge_text}**: {display_title}")

            # 2-Column Display
            left_col, right_col = st.columns([1, 1], gap="large")

            with left_col:
                st.subheader("📖 விரிவான விளக்கம்" if is_tamil else "📖 Detailed Explanation")
                st.write(result.main_answer)

                st.subheader("🔬 முக்கிய காரணங்கள் / காரணிகள்" if is_tamil else "🔬 Causes & Biological Mechanisms")
                for point in result.detailed_points:
                    st.markdown(f"- {point}")

                st.subheader("⚡ முன்னெச்சரிக்கைகள் & குறிப்புகள்" if is_tamil else "⚡ Precautions & Lifestyle Tips")
                for item in result.triggers_or_precautions:
                    st.markdown(f"- {item}")

                st.subheader("📋 மருத்துவ வழிகாட்டுதல்" if is_tamil else "📋 Doctor Advice / Questions")
                for q in result.doctor_advice_or_questions:
                    st.markdown(f"- {q}")

            with right_col:
                st.subheader("🎥 விளக்க வீடியோ (Educational Video)")
                st.video(video_url)
                st.markdown(f"👉 [யூடியூபில் பார்க்க / Open in YouTube]({video_url})")
                st.caption(f"Topic: **{display_title}**")

st.divider()
st.caption("⚠️ **மருத்துவ மறுப்பு (Disclaimer)**: இந்த செயலி கல்வி மற்றும் தகவல் நோக்கங்களுக்காக மட்டுமே. தகுந்த மருத்துவ ஆலோசனையை பெற எப்போதும் மருத்துவரை அணுகவும்.")
