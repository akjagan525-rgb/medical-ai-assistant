exports.handler = async function(event, context) {
  if (event.httpMethod !== "POST") {
    return { statusCode: 405, body: "Method Not Allowed" };
  }

  const headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Content-Type": "application/json"
  };

  try {
    const { query, language } = JSON.parse(event.body);
    const API_KEY = process.env.GEMINI_API_KEY;

    if (!API_KEY) {
      return {
        statusCode: 500,
        headers,
        body: JSON.stringify({ error: "API key not configured in Netlify Environment Variables." })
      };
    }

    const prompt = `
    You are a friendly, helpful AI assistant who is also an expert Doctor and Science Explainer.
    
    The user said: "${query}"
    Language to respond in: ${language}
    
    STEP 1 - Classify the message into ONE of these types:
    - "greeting": Hi, hello, how are you, good morning, thanks, etc.
    - "general_chat": General conversation not related to health or science.
    - "medical_or_science": Health symptoms, body questions, science curiosities, medical conditions, diet, wellness, etc.
    
    STEP 2 - Based on the type, respond DIFFERENTLY:
    
    If type is "greeting" or "general_chat":
    Return this JSON:
    {
      "type": "chat",
      "title_en": "Hello!",
      "title_ta": "வணக்கம்!",
      "answer": "A warm, friendly conversational reply in ${language}. If greeting, say hello back and briefly mention you can answer any medical, health or science question.",
      "why_it_happens": [],
      "fun_fact_or_tip": "",
      "youtube_search": ""
    }
    
    If type is "medical_or_science":
    Return this JSON:
    {
      "type": "medical",
      "title_en": "Title in English",
      "title_ta": "Title in Tamil (தமிழ்)",
      "answer": "Clear, engaging 2-sentence explanation in ${language}",
      "why_it_happens": ["Biological/scientific cause 1 in ${language}", "Cause 2 in ${language}", "Cause 3 in ${language}"],
      "fun_fact_or_tip": "1 fun fact or tip in ${language}",
      "youtube_search": "Exact YouTube search query for this topic"
    }
    
    Output ONLY valid JSON. No markdown. No extra text.
    `;

    const models = [
      "gemini-3.6-flash",
      "gemini-flash-latest",
      "gemini-2.0-flash"
    ];

    let lastError = null;
    for (const model of models) {
      try {
        const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${API_KEY}`;

        const response = await fetch(url, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            contents: [{ parts: [{ text: prompt }] }],
            generationConfig: { responseMimeType: "application/json" }
          })
        });

        if (!response.ok) {
          const err = await response.json();
          throw new Error(err.error?.message || "Model unavailable");
        }

        const data = await response.json();

        if (!data.candidates || !data.candidates[0]) {
          throw new Error("No response from model");
        }

        const rawText = data.candidates[0].content.parts[0].text;
        const parsed = JSON.parse(rawText);

        return {
          statusCode: 200,
          headers,
          body: JSON.stringify(parsed)
        };

      } catch (e) {
        lastError = e;
        continue;
      }
    }

    throw lastError;

  } catch (error) {
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ error: error.message })
    };
  }
};
