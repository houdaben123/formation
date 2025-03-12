import streamlit as st
import pandas as pd
import google.generativeai as genai
import os

# إعداد API لـ Gemini
API_KEY = "AIzaSyBfyyQwcKpcJRWtwuOTWkIOu1z7P8C4Y20"  # استبدل هذا بمفتاح API الخاص بك
os.environ["GOOGLE_API_KEY"] = API_KEY
genai.configure(api_key=API_KEY)


# وظيفة تحليل المشاعر لكل التعليقات دفعة واحدة
def analyze_sentiment_batch(texts):
    if not texts:
        return ["❌ لا يوجد نص لتحليله"] * len(texts)

    combined_text = "\n\n".join([f"تعليق {i + 1}: {text}" for i, text in enumerate(texts)])
    prompt = f"حلل مشاعر التعليقات التالية بشكل موجز وأعطِ نتيجة لكل تعليق ثم ضع في جدول رقم التعليق والعلامة 1 للتعليق الاجابي والعلامة 0 للتعليق السلبي:{combined_text}"

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text if response else ["❌ تعذر التحليل"] * len(texts)
    except Exception as e:
        return [f"⚠️ خطأ: {str(e)}"] * len(texts)


# واجهة Streamlit
st.title("🔍 تحليل مشاعر التعليقات دفعة واحدة باستخدام Gemini")

# تحميل الملف
uploaded_file = st.file_uploader("📂 قم بتحميل ملف التعليقات (CSV, Excel, TXT):", type=["csv", "xlsx", "xls", "txt"])

if uploaded_file:
    # تحديد نوع الملف وقراءته
    file_extension = uploaded_file.name.split(".")[-1]

    if file_extension in ["csv"]:
        df = pd.read_csv(uploaded_file)
    elif file_extension in ["xlsx", "xls"]:
        df = pd.read_excel(uploaded_file)
    elif file_extension in ["txt"]:
        df = pd.read_csv(uploaded_file, delimiter="\n", header=None, names=["التعليق"])
    else:
        st.error("❌ نوع الملف غير مدعوم!")
        st.stop()

    # عرض البيانات الأولية
    st.write("📌 **أول 5 تعليقات في الملف:**")
    st.write(df.head())

    # اختيار العمود الذي يحتوي على التعليقات
    column_name = st.selectbox("📝 اختر العمود الذي يحتوي على التعليقات:", df.columns)

    if st.button("⚡ تحليل جميع المشاعر دفعة واحدة"):
        with st.spinner("🚀 جارٍ تحليل المشاعر..."):
            comments = df[column_name].dropna().astype(str).tolist()  # إزالة القيم الفارغة
            sentiments = analyze_sentiment_batch(comments)
            # df["تحليل المشاعر"] = sentiments[: len(df)]  # التأكد من تطابق الطول

        # عرض النتائج
        st.write("📊 **نتائج تحليل المشاعر:**")
        st.write(sentiments)

        # تحميل النتائج كملف CSV
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 تحميل النتائج كملف CSV", csv, "تحليل_المشاعر.csv", "text/csv")
