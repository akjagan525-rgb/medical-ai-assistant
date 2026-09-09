import urllib.parse
import streamlit as st
from analyzer import analyze_symptoms

st.set_page_config(
    page_title="AI Doctor & Science Explainer",
    page_icon="⚡",
    layout="wide"
)

# Header & Language Choice
top_col1, top_col2 = st.columns([3, 1])
with top_col1:
    st.title("⚡ AI மருத்துவர் & அறிவியல் விளக்கம்")
    st.write("மருத்துவ அறிகுறிகள் அல்லது எந்த ஒரு விசித்திரமான கேள்வியையும் கேளுங்கள் — **1 வினாடியில் பதில் & வீடியோ!**")
with top_col2:
    language = st.selectbox("🌐 மொழி / Language:", ["Tamil (தமிழ்)", "English"])

is_tamil = "Tamil" in language
lang_code = "Tamil" if is_tamil else "English"

# Fun Silly & Medical Examples
st.markdown("**வேடிக்கையான & மருத்துவ கேள்விகள் / Try These:**")
q1, q2, q3, q4 = st.columns(4)
preset_text = ""

if is_tamil:
    if q1.button("🥱 கொட்டாவி ஏன் வருது?"):
        preset_text = "மனிதர்களுக்கு கொட்டாவி (yawn) ஏன் வருகிறது? ஒருவரை பார்த்தால் நமக்கும் ஏன் வருகிறது?"
    if q2.button("🧅 வெங்காயம் நறுக்கினா ஏன் அழுகை?"):
        preset_text = "வெங்காயம் நறுக்கும்போது கண்களில் ஏன் தண்ணீர் வருகிறது?"
    if q3.button("💨 விக்கல் (Hiccup) ஏன் வருகிறது?"):
        preset_text = "விக்கல் ஏன் வருகிறது? அதை உடனே நிறுத்த என்ன செய்ய வேண்டும்?"
    if q4.button("🔥 நெஞ்செரிச்சல் (Acid Reflux)"):
        preset_text = "சாப்பிட்ட பிறகு நெஞ்சில் கடுமையான எரிச்சல் மற்றும் புளித்த ஏப்பம் வருவது ஏன்?"
else:
    if q1.button("🥱 Why do we yawn?"):
        preset_text = "Why do humans yawn and why is it contagious?"
    if q2.button("🧅 Why do onions make us cry?"):
        preset_text = "Why do onions make our eyes water when cutting them?"
    if q3.button("💨 Why do we get hiccups?"):
        preset_text = "Why do we get hiccups and how to stop them instantly?"
    if q4.button("🔥 Acid Reflux / GERD"):
        preset_text = "Burning pain in chest and acid taste after eating."

# Input Box
input_label = "உங்கள் கேள்வி (எந்த வேடிக்கையான கேள்வியானாலும் கேட்கலாம்):" if is_tamil else "Ask ANY question (even silly, funny body questions):"
user_query = st.text_area(
    input_label,
    value=preset_text,
    placeholder="உதாரணம்: விக்கல் ஏன் வருது? / தூக்கத்துல ஏன் கனவு வருது? / தலைவலி ஏன் வருது?" if is_tamil else "e.g. Why do we sneeze? / Why do we dream? / Why do our fingers wrinkle in water?",
    height=80
)

if st.button("⚡ உடனடி பதில் & வீடியோ காண்க (Get Answer)", type="primary"):
    if not user_query.strip():
        st.warning("தயவுசெய்து ஏதேனும் கேள்வியை தட்டச்சு செய்யவும்." if is_tamil else "Please type a question first.")
    else:
        with st.spinner("விளக்கம் தயாராகிறது..." if is_tamil else "Answering instantly..."):
            result = analyze_symptoms(user_query, language=lang_code)

            if result.is_emergency:
                st.error(f"🚨 **அவசர எச்சரிக்கை / EMERGENCY WARNING**: {result.emergency_warning}")
                st.stop()

            display_title = f"{result.title_ta} ({result.title_en})" if is_tamil else f"{result.title_en}"
            st.success(f"💡 **{display_title}**")

            # 2-Column Fast Layout
            left_col, right_col = st.columns([3, 2], gap="large")

            with left_col:
                st.subheader("📖 எளிய பதில்" if is_tamil else "📖 Quick Answer")
                st.write(result.answer)

                st.subheader("🔬 அறிவியல் & உயிரியல் காரணம்" if is_tamil else "🔬 Why It Happens (Science)")
                for point in result.why_it_happens:
                    st.markdown(f"- {point}")

                st.subheader("💡 சுவாரஸ்யமான உண்மை / குறிப்பு" if is_tamil else "💡 Fun Fact / Tip")
                st.info(result.fun_fact_or_tip)

            with right_col:
                st.subheader("🎥 இதற்கான வீடியோ (Video for this topic)")
                
                # Dynamic YouTube search query
                encoded_query = urllib.parse.quote(result.youtube_search)
                direct_youtube_url = f"https://www.youtube.com/results?search_query={encoded_query}"

                st.markdown(f"""
                <div style="background:#1E1E1E;padding:18px;border-radius:12px;border:1px solid #333;text-align:center;">
                    <p style="color:#FFF;font-size:16px;margin-bottom:12px;">
                        🎬 <b>{result.youtube_search}</b>
                    </p>
                    <a href="{direct_youtube_url}" target="_blank" style="text-decoration:none;">
                        <button style="background-color:#FF0000;color:white;padding:14px 22px;border:none;border-radius:8px;font-size:16px;font-weight:bold;cursor:pointer;width:100%;">
                            ▶️ {'யூடியூபில் வீடியோ பார்க்க கிளிக் செய்க' if is_tamil else '▶️ Watch Top Videos on YouTube'}
                        </button>
                    </a>
                </div>
                """, unsafe_allow_html=True)
                st.caption("Opens the best Tamil/English explanation videos on YouTube instantly.")

st.divider()
st.caption("⚡ Powered by Gemini Flash • Zero lag • Answers all medical & curious questions.")
