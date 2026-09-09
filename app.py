import streamlit as st
from analyzer import analyze_symptoms
from video_service import get_video_data

st.set_page_config(
    page_title="AI Doctor & Science Explainer (தமிழ் / English)",
    page_icon="🩺",
    layout="wide"
)

# Header & Language Choice
top_col1, top_col2 = st.columns([3, 1])
with top_col1:
    st.title("🩺 AI மருத்துவ & அறிவியல் உதவியாளர்")
    st.write("மருத்துவ அறிகுறிகள், உடல் சார்ந்த சந்தேகங்கள் அல்லது ஏதேனும் சுவாரஸ்யமான கேள்விகளைக் கேளுங்கள் — உடனடி பதில் & வீடியோவை தமிழில் பெறுங்கள்!")
with top_col2:
    language = st.selectbox("🌐 மொழி / Language:", ["Tamil (தமிழ்)", "English"])

is_tamil = "Tamil" in language
lang_code = "Tamil" if is_tamil else "English"

# Fun & Medical Sample Buttons
st.markdown("**மாதிரிகள் / Try Asking:**")
q1, q2, q3 = st.columns(3)
preset_text = ""

if is_tamil:
    if q1.button("🧅 வெங்காயம் நறுக்கும்போது ஏன் கண்ணீர் வருகிறது?"):
        preset_text = "வெங்காயம் நறுக்கும்போது கண்களில் ஏன் தண்ணீர் வருகிறது? அதன் அறிவியல் காரணம் என்ன?"
    if q2.button("🥱 கொட்டாவி ஏன் வருகிறது?"):
        preset_text = "மனிதர்களுக்கு கொட்டாவி (yawn) ஏன் வருகிறது? ஒருவரைப் பார்த்தால் நமக்கும் ஏன் வருகிறது?"
    if q3.button("🔥 நெஞ்செரிச்சல் (Acid Reflux)"):
        preset_text = "சாப்பிட்ட பிறகு நெஞ்சில் கடுமையான எரிச்சல் மற்றும் புளித்த ஏப்பம் வருகிறது. என்ன காரணம்?"
else:
    if q1.button("🧅 Why do onions make us cry?"):
        preset_text = "Why do onions make our eyes water when cutting them? What is the chemical reason?"
    if q2.button("🥱 Why do humans yawn?"):
        preset_text = "Why do we yawn, and why is yawning contagious when we see someone else do it?"
    if q3.button("🔥 Heartburn / Acid Reflux"):
        preset_text = "Burning pain behind breastbone after meals and acid regurgitation. What causes this?"

# Input Box
input_label = "உங்கள் கேள்வி அல்லது அறிகுறிகளை தட்டச்சு செய்யவும் (எந்த கேள்வியானாலும் கேட்கலாம்):" if is_tamil else "Ask ANY question, silly curious inquiry, or medical symptoms:"
user_query = st.text_area(
    input_label,
    value=preset_text,
    placeholder="உதாரணம்: கொட்டாவி ஏன் வருது? / தலைவலி ஏன் வருது? / தூக்கத்தில் ஏன் கனவு காண்கிறோம்?" if is_tamil else "e.g. Why do we sneeze? / Why do we get headaches? / Why is blood red?",
    height=90
)

btn_label = "🔍 பதில் & வீடியோவை காண்க" if is_tamil else "🔍 Get Answer & Video"

if st.button(btn_label, type="primary"):
    if not user_query.strip():
        st.warning("தயவுசெய்து ஏதேனும் கேள்வியை தட்டச்சு செய்யவும்." if is_tamil else "Please type a question or symptoms first.")
    else:
        with st.spinner("விளக்கம் மற்றும் வீடியோ தயாராகிறது..." if is_tamil else "Finding answer and video..."):
            result = analyze_symptoms(user_query, language=lang_code)

            if result.is_emergency:
                st.error(f"🚨 **அவசர எச்சரிக்கை / EMERGENCY WARNING**: {result.emergency_warning}")
                st.stop()

            display_title = f"{result.title_ta} ({result.title_en})" if is_tamil else f"{result.title_en}"
            st.success(f"💡 **[{result.category}]**: {display_title}")

            # 2-Column Layout
            left_col, right_col = st.columns([1, 1], gap="large")

            with left_col:
                st.subheader("📖 எளிய விளக்கம்" if is_tamil else "📖 Explanation")
                st.write(result.main_answer)

                st.subheader("🔬 அறிவியல் / உயிரியல் காரணங்கள்" if is_tamil else "🔬 Scientific & Biological Reasons")
                for point in result.reasons_or_points:
                    st.markdown(f"- {point}")

                st.subheader("💡 சுவாரஸ்யமான தகவல்கள் & குறிப்புகள்" if is_tamil else "💡 Fun Facts & Tips")
                for item in result.fun_facts_or_tips:
                    st.markdown(f"- {item}")

            with right_col:
                st.subheader("🎥 இதற்கான வீடியோ (Video for this topic)")
                
                search_query = result.tamil_video_search if is_tamil else result.english_video_search
                embed_url, direct_youtube_url = get_video_data(search_query, result.title_en)

                st.video(embed_url)

                st.markdown(f"""
                <a href="{direct_youtube_url}" target="_blank" style="text-decoration:none;">
                    <div style="background-color:#FF0000;color:white;padding:12px;border-radius:8px;text-align:center;font-weight:bold;margin-top:10px;">
                        ▶️ {'இதற்கான தமிழ் வீடியோக்களை நேரடியாக யூடியூபில் பார்க்க' if is_tamil else '▶️ Watch Top Videos for this on YouTube'}
                    </div>
                </a>
                """, unsafe_allow_html=True)
                st.caption(f"Topic: **{search_query}**")

st.divider()
st.caption("⚠️ **மருத்துவ மறுப்பு (Disclaimer)**: இந்த செயலி கல்வி மற்றும் அறிவியல் தகவல் நோக்கங்களுக்காக மட்டுமே.")
